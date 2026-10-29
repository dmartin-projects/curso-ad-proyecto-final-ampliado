# asistente/application/agent/contexto_pregunta.py — quién pregunta, sobre qué hogar y qué día es allí (módulo 94)
from dataclasses import dataclass
from datetime import date
from zoneinfo import ZoneInfo

from asistente.application.ports.i_membresias import IMembresias
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from core.application.ports.i_reloj import IReloj
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor


@dataclass(frozen=True, slots=True)
class ContextoPregunta:
    """Lo reciben TODAS las tools. Lo construye el adapter de entrada con la identidad de la SESIÓN, nunca con algo
    que diga el modelo: las tools no tienen un argumento hogar_id, así que el modelo no puede pedir otro hogar (ni
    equivocándose ni convencido por un texto malicioso, módulo 102)."""

    usuario_id: int
    hogar: HogarDelUsuario
    actor: Actor  # limitado a LECTOR: el agente solo lee (los cambios, con confirmación: módulo 97)
    hoy: date  # en la zona horaria del HOGAR: "este mes" es el suyo

    @classmethod
    def abrir(cls, *, usuario_id: int, hogar_id: int, membresias: IMembresias, reloj: IReloj) -> "ContextoPregunta":
        hogar = membresias.hogar_de(usuario_id, hogar_id)
        if hogar is None:  # el mismo error exista o no: no se revela qué hogares hay (como el 404 de la API)
            raise SinPermisoException("El hogar no existe o no eres miembro.")
        # Privilegios mínimos: aunque seas administrador, el agente pide los use cases como LECTOR. Si una tool tuviera
        # un fallo y llamara a un comando, el propio use case lo rechazaría.
        actor = Actor(usuario_id=usuario_id, rol=Rol(hogar.rol)).limitado_a(Rol.LECTOR)
        hoy = reloj.ahora().astimezone(ZoneInfo(hogar.zona_horaria)).date()
        return cls(usuario_id=usuario_id, hogar=hogar, actor=actor, hoy=hoy)
