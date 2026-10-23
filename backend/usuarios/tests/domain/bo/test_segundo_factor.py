"""Las reglas del segundo factor de una cuenta (módulo 92), sin base de datos."""

from datetime import UTC, datetime, timedelta

import pytest

from usuarios.domain.bo.segundo_factor import SegundoFactor
from usuarios.domain.enums.aviso_de_fallos import AvisoDeFallos
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.mfa_no_activo_exception import MfaNoActivoException
from usuarios.domain.exceptions.mfa_ya_activo_exception import MfaYaActivoException
from usuarios.domain.exceptions.segundo_factor_bloqueado_exception import SegundoFactorBloqueadoException
from usuarios.domain.exceptions.segundo_factor_bloqueado_hasta_recuperar_exception import (
    SegundoFactorBloqueadoHastaRecuperarException,
)
from usuarios.domain.services.bloqueo_progresivo import TECHO_DE_FALLOS, espera_tras

AHORA = datetime(2026, 10, 23, 10, 0, tzinfo=UTC)


def test_un_codigo_vale_una_vez_y_ninguno_anterior():
    segundo = SegundoFactor(1, "SECRETO", activo=True)
    segundo.aceptar(1000)
    for repetido_o_anterior in (1000, 999):
        with pytest.raises(CodigoNoValidoException):
            segundo.aceptar(repetido_o_anterior)
    segundo.aceptar(1001)  # el siguiente, sí


def test_activar_y_desactivar():
    segundo = SegundoFactor(1)
    segundo.empezar("SECRETO")
    segundo.confirmar(1000)
    assert segundo.activo
    with pytest.raises(MfaYaActivoException):
        segundo.empezar("OTRO")  # con el MFA activo, un secreto nuevo no: antes, desactivarlo (step-up)
    segundo.desactivar()
    assert (segundo.activo, segundo.secreto, segundo.ultimo_paso) == (False, None, None)
    with pytest.raises(MfaNoActivoException):
        segundo.desactivar()


def test_bloqueo_progresivo():
    assert [espera_tras(n) for n in (4, 5, 10, 15, 20, 50)] == [
        timedelta(0), timedelta(minutes=1), timedelta(minutes=2), timedelta(minutes=4), timedelta(minutes=8),
        timedelta(hours=1),  # el techo
    ]  # fmt: skip
    segundo = SegundoFactor(1)
    for _ in range(4):
        segundo.anotar_fallo(AHORA)
    segundo.exigir_desbloqueado(AHORA)  # 4 fallos: aún nada
    segundo.anotar_fallo(AHORA)
    with pytest.raises(SegundoFactorBloqueadoException) as error:
        segundo.exigir_desbloqueado(AHORA + timedelta(seconds=30))
    assert error.value.contexto == {"segundos": 31}
    segundo.exigir_desbloqueado(AHORA + timedelta(minutes=1))
    segundo.anotar_acierto()
    assert (segundo.fallos, segundo.bloqueado_hasta) == (0, None)


def test_el_techo_bloquea_hasta_recuperar_la_cuenta_y_avisa():
    """NIST SP 800-63B-4: como mucho 100 fallos seguidos. Antes del techo, avisos: a los 5 (alguien tiene la
    contraseña) y al llegar (bloqueado). Después, ni esperando: solo recuperando la cuenta."""
    segundo = SegundoFactor(1)
    avisos = [segundo.anotar_fallo(AHORA) for _ in range(TECHO_DE_FALLOS)]
    assert avisos[4] is AvisoDeFallos.INTENTOS and avisos[-1] is AvisoDeFallos.BLOQUEO
    assert [a for a in avisos if a is not None] == [AvisoDeFallos.INTENTOS, AvisoDeFallos.BLOQUEO]
    for despues in (timedelta(hours=1), timedelta(days=365)):
        with pytest.raises(SegundoFactorBloqueadoHastaRecuperarException) as error:
            segundo.exigir_desbloqueado(AHORA + despues)
        assert "segundos" not in error.value.contexto  # sin Retry-After: esperar no sirve
    segundo.desbloquear()
    segundo.exigir_desbloqueado(AHORA)
    assert (segundo.fallos, segundo.bloqueado_hasta) == (0, None)
