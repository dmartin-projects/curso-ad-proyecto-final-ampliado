# hogares/domain/bo/invitacion.py — entrar en un hogar por invitación (módulos 71 y 88)
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar

from core.domain.enums.rol import Rol
from hogares.domain.bo.membresia import Membresia
from hogares.domain.exceptions.invitacion_no_valida_exception import InvitacionNoValidaException

VIGENCIA_INVITACION = timedelta(days=7)


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def token_de_invitacion() -> str:
    return secrets.token_urlsafe(32)


@dataclass(eq=False)
class Invitacion:
    hogar_id: int
    email: str
    rol: Rol
    caduca: datetime
    invitado_por_id: int | None = None
    token: str = ""
    aceptada: datetime | None = None
    id: int | None = None

    tipo: ClassVar[str] = "hogares.invitacion"

    def __post_init__(self):
        self.email = normalizar_email(self.email)
        self.rol = Rol(self.rol)
        self.token = self.token or token_de_invitacion()

    @classmethod
    def nueva(
        cls, *, hogar_id: int, email: str, rol: Rol, invitado_por_id: int | None, ahora: datetime
    ) -> "Invitacion":
        return cls(
            hogar_id=hogar_id, email=email, rol=rol, invitado_por_id=invitado_por_id, caduca=ahora + VIGENCIA_INVITACION
        )

    def renovar(self, *, rol: Rol, invitado_por_id: int | None, ahora: datetime) -> None:
        """Invitar otra vez al mismo email: la misma invitación, con el rol nuevo y otros siete días."""
        self.rol, self.invitado_por_id, self.caduca = Rol(rol), invitado_por_id, ahora + VIGENCIA_INVITACION

    def vigente(self, ahora: datetime) -> bool:
        return self.aceptada is None and self.caduca > ahora

    def aceptar(self, *, usuario_id: int, email: str, ahora: datetime) -> Membresia:
        """Solo la persona invitada (su email), una vez y antes de que caduque."""
        if not self.vigente(ahora) or self.email != normalizar_email(email):
            raise InvitacionNoValidaException()
        self.aceptada = ahora
        return Membresia(hogar_id=self.hogar_id, usuario_id=usuario_id, rol=self.rol)
