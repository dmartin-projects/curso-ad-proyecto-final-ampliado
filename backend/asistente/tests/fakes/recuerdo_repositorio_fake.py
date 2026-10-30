# asistente/tests/fakes/recuerdo_repositorio_fake.py (módulo 99)
from asistente.domain.exceptions.recuerdo_no_encontrado_exception import RecuerdoNoEncontradoException
from asistente.domain.read_models.recuerdo_listado import RecuerdoListado
from asistente.domain.repositories.i_recuerdo_command_repository import IRecuerdoCommandRepository
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class RecuerdoRepositorioFake(AlmacenEnMemoria, IRecuerdoCommandRepository, IRecuerdoQueryService):
    def obtener(self, usuario_id, hogar_id, recuerdo_id):
        r = self._datos.get(recuerdo_id)
        if r is None or (r.usuario_id, r.hogar_id) != (usuario_id, hogar_id):
            raise RecuerdoNoEncontradoException()
        return copia(r)

    def guardar(self, recuerdo):
        self._asignar_id(recuerdo)
        self._datos[recuerdo.id] = copia(recuerdo)

    def eliminar(self, recuerdo):
        self._datos.pop(recuerdo.id, None)

    def contar(self, usuario_id, hogar_id):
        return len(self._de(usuario_id, hogar_id))

    def listar(self, usuario_id, hogar_id):
        return tuple(RecuerdoListado(r.id, r.texto, r.creado) for r in self._de(usuario_id, hogar_id))

    def _de(self, usuario_id, hogar_id):
        return [r for r in self._datos.values() if (r.usuario_id, r.hogar_id) == (usuario_id, hogar_id)]
