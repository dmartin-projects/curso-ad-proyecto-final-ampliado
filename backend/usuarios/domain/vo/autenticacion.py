# usuarios/domain/vo/autenticacion.py — cómo y cuándo se ha autenticado una sesión (módulo 92)
from dataclasses import dataclass
from datetime import datetime, timedelta

from usuarios.domain.enums.factor import Factor
from usuarios.domain.services.factores import ACR_MULTIFACTOR, ACR_UN_FACTOR, AMR, PRIMEROS_FACTORES, SEGUNDOS_FACTORES


@dataclass(frozen=True, slots=True)
class Autenticacion:
    """Cómo se abrió (o se renovó con un step-up) una sesión: los factores y el momento (el `auth_time` de OIDC)."""

    factores: frozenset[Factor]
    momento: datetime
    passkey_sincronizada: bool = False  # una passkey en iCloud o Google: la clave sale del dispositivo ("swk")

    @property
    def multifactor(self) -> bool:
        """Dos factores de TIPOS distintos: uno de los primeros más uno de los segundos (algo que sabes + algo que
        tienes). Contraseña y proveedor no lo son: los dos acaban en "una contraseña", la de Gastos o la de Google, y
        la política es que el MFA del proveedor no cuenta. Una passkey sola, sí: al entrar sin contraseña se exige
        verificación del usuario (huella, PIN), y es algo que tienes + algo que eres o sabes en un gesto."""
        if self.factores == {Factor.PASSKEY}:
            return True
        return bool(self.factores & PRIMEROS_FACTORES) and bool(self.factores & SEGUNDOS_FACTORES)

    def amr(self) -> list[str]:
        valores = {AMR[f] for f in self.factores if f in AMR}
        if Factor.PASSKEY in self.factores:
            valores |= {"swk" if self.passkey_sincronizada else "hwk", "user"}
        return sorted(valores | ({"mfa"} if self.multifactor else set()))

    def acr(self) -> str:
        return ACR_MULTIFACTOR if self.multifactor else ACR_UN_FACTOR

    def reciente(self, ahora: datetime, segundos: int) -> bool:
        """Para el step-up: ¿se autenticó hace menos de `segundos`?"""
        return ahora - self.momento <= timedelta(seconds=segundos)

    def con(self, factor: Factor, momento: datetime, *, sincronizada: bool = False) -> "Autenticacion":
        """La misma sesión tras demostrar otro factor (el segundo, o un step-up): el momento es el de ahora."""
        return Autenticacion(self.factores | {factor}, momento, self.passkey_sincronizada or sincronizada)
