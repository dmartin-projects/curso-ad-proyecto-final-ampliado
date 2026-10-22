# hogares/tests/fakes/membresia_command_repository_fake.py — IMembresiaCommandRepository en memoria (módulo 88)
from core.domain.enums.rol import Rol
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from hogares.domain.bo.membresia import Membresia
from hogares.domain.exceptions.miembro_no_encontrado_exception import MiembroNoEncontradoException
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository


class MembresiaCommandRepositoryFake(AlmacenEnMemoria, IMembresiaCommandRepository):
    def __init__(self, emails: dict[int, str] | None = None):
        super().__init__()
        self.emails = emails or {}  # usuario_id → email (lo que en el ORM es un JOIN con usuarios)

    def obtener(self, hogar_id, membresia_id, *, bloquear=False):
        m = self._datos.get(membresia_id)
        if m is None or m.hogar_id != hogar_id:
            raise MiembroNoEncontradoException()
        return copia(m)

    def admins(self, hogar_id):
        return sum(1 for m in self._datos.values() if m.hogar_id == hogar_id and m.rol == Rol.ADMIN)

    def es_miembro(self, hogar_id, *, usuario_id=None, email=None):
        return any(
            m.hogar_id == hogar_id
            and (m.usuario_id == usuario_id or self.emails.get(m.usuario_id, "").lower() == email)
            for m in self._datos.values()
        )

    def guardar(self, membresia):
        if any((m.hogar_id, m.usuario_id) == (membresia.hogar_id, membresia.usuario_id) and m.id != membresia.id
               for m in self._datos.values()):  # fmt: skip
            raise YaEsMiembroException()  # la UniqueConstraint membresia_unica
        self._asignar_id(membresia)
        self._datos[membresia.id] = copia(membresia)

    def eliminar(self, membresia):
        self._datos.pop(membresia.id, None)

    def de(self, hogar_id) -> list[Membresia]:
        return [m for m in self.todos() if m.hogar_id == hogar_id]
