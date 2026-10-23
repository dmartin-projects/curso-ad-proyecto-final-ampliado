# usuarios/domain/bo/segundo_factor.py — el segundo factor de una cuenta (módulo 92)
#
# Cómo se ha autenticado alguien (con qué factores y cuándo), cuándo hace falta un segundo factor, qué hace falta para
# que un código TOTP valga (una vez, en su ventana) y cómo se frena a quien prueba códigos. La criptografía (RFC 6238,
# WebAuthn, el cifrado del secreto) es de los adapters; las reglas, de aquí.
from dataclasses import dataclass
from datetime import datetime

from usuarios.domain.enums.aviso_de_fallos import AvisoDeFallos
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.mfa_no_activo_exception import MfaNoActivoException
from usuarios.domain.exceptions.mfa_ya_activo_exception import MfaYaActivoException
from usuarios.domain.exceptions.segundo_factor_bloqueado_exception import SegundoFactorBloqueadoException
from usuarios.domain.exceptions.segundo_factor_bloqueado_hasta_recuperar_exception import (
    SegundoFactorBloqueadoHastaRecuperarException,
)
from usuarios.domain.services.bloqueo_progresivo import FALLOS_POR_TRAMO, TECHO_DE_FALLOS, espera_tras


@dataclass(eq=False)
class SegundoFactor:
    """El segundo factor de una cuenta: su TOTP y el contador de fallos (de cualquier segundo factor).

    El secreto está aquí en claro: lo cifra el repositorio al guardarlo (y lo descifra al leerlo).
    """

    usuario_id: int
    secreto: str | None = None  # base32 (RFC 4648), el que se enseña en el QR
    activo: bool = False  # el TOTP se ha confirmado con un primer código: el MFA está activo
    ultimo_paso: int | None = None  # el paso de 30 s del último código aceptado (RFC 6238 §5.2: un solo uso)
    fallos: int = 0  # seguidos, de cualquier segundo factor
    bloqueado_hasta: datetime | None = None

    def empezar(self, secreto: str) -> None:
        """Un secreto nuevo, pendiente de confirmar. Con el MFA ya activo, no: hay que desactivarlo antes."""
        if self.activo:
            raise MfaYaActivoException()
        self.secreto, self.ultimo_paso = secreto, None

    def confirmar(self, paso: int) -> None:
        if self.activo:
            raise MfaYaActivoException()
        self.aceptar(paso)
        self.activo = True

    def desactivar(self) -> None:
        if not self.activo:
            raise MfaNoActivoException()
        self.secreto, self.activo, self.ultimo_paso = None, False, None

    def aceptar(self, paso: int) -> None:
        """Un código vale una vez: el de un paso ya usado (o anterior) es un código visto, no uno nuevo."""
        if self.ultimo_paso is not None and paso <= self.ultimo_paso:
            raise CodigoNoValidoException()
        self.ultimo_paso = paso

    def exigir_desbloqueado(self, ahora: datetime) -> None:
        if self.fallos >= TECHO_DE_FALLOS:
            raise SegundoFactorBloqueadoHastaRecuperarException()
        if self.bloqueado_hasta is not None and ahora < self.bloqueado_hasta:
            raise SegundoFactorBloqueadoException(segundos=int((self.bloqueado_hasta - ahora).total_seconds()) + 1)

    def anotar_fallo(self, ahora: datetime) -> AvisoDeFallos | None:
        self.fallos += 1
        if self.fallos >= TECHO_DE_FALLOS:  # ya no hay espera que valga: hasta recuperar la cuenta
            return AvisoDeFallos.BLOQUEO if self.fallos == TECHO_DE_FALLOS else None
        if self.fallos % FALLOS_POR_TRAMO == 0:  # cada 5 fallos seguidos, una espera (cada vez, el doble)
            self.bloqueado_hasta = ahora + espera_tras(self.fallos)
        return AvisoDeFallos.INTENTOS if self.fallos == FALLOS_POR_TRAMO else None

    def anotar_acierto(self) -> None:
        self.fallos, self.bloqueado_hasta = 0, None

    def desbloquear(self) -> None:
        """Al recuperar la cuenta (ConfirmarRecuperacionUseCase): la persona ha demostrado que el email es suyo y la
        contraseña ya es otra. Los fallos empiezan de cero."""
        self.anotar_acierto()
