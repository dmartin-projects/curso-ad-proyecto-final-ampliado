# asistente/tests/fakes/membresias_fake.py — IMembresias en memoria (módulos 94 y 97)
from asistente.application.ports.i_membresias import IMembresias
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from asistente.domain.read_models.miembro_del_hogar import MiembroDelHogar
from core.domain.enums.rol import Rol


class MembresiasFake(IMembresias):
    """{(usuario_id, hogar_id): HogarDelUsuario}: si la pareja no está, no es miembro."""

    def __init__(self, hogares: dict[tuple[int, int], HogarDelUsuario] | None = None):
        self.hogares = dict(hogares or {})
        self.miembros_por_hogar: dict[int, tuple[MiembroDelHogar, ...]] = {}

    def hogar_de(self, usuario_id, hogar_id):
        return self.hogares.get((usuario_id, hogar_id))

    def miembros(self, actor, hogar_id):
        actor.exigir(Rol.LECTOR)
        return self.miembros_por_hogar.get(hogar_id, ())
