# asistente/tests/fakes/membresias_fake.py — IMembresias en memoria (módulo 94)
from asistente.application.ports.i_membresias import IMembresias
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario


class MembresiasFake(IMembresias):
    """{(usuario_id, hogar_id): HogarDelUsuario}: si la pareja no está, no es miembro."""

    def __init__(self, hogares: dict[tuple[int, int], HogarDelUsuario] | None = None):
        self.hogares = dict(hogares or {})

    def hogar_de(self, usuario_id, hogar_id):
        return self.hogares.get((usuario_id, hogar_id))
