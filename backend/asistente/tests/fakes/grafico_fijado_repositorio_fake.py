# asistente/tests/fakes/grafico_fijado_repositorio_fake.py (módulo 97)
from asistente.domain.exceptions.grafico_no_encontrado_exception import GraficoNoEncontradoException
from asistente.domain.read_models.grafico_fijado_listado import GraficoFijadoListado
from asistente.domain.repositories.i_grafico_fijado_command_repository import IGraficoFijadoCommandRepository
from asistente.domain.repositories.i_grafico_fijado_query_service import IGraficoFijadoQueryService
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class GraficoFijadoRepositorioFake(AlmacenEnMemoria, IGraficoFijadoCommandRepository, IGraficoFijadoQueryService):
    """Los dos lados (escribir y leer) sobre el mismo almacén: lo que se fija se ve al listar."""

    def obtener(self, hogar_id, grafico_id):
        g = self._datos.get(grafico_id)
        if g is None or g.hogar_id != hogar_id:
            raise GraficoNoEncontradoException()
        return copia(g)

    def guardar(self, grafico):
        self._asignar_id(grafico)
        self._datos[grafico.id] = copia(grafico)

    def eliminar(self, grafico):
        self._datos.pop(grafico.id, None)

    def listar(self, hogar_id):
        return tuple(
            GraficoFijadoListado(g.id, g.especificacion, f"usuario {g.usuario_id}", None)
            for g in self._datos.values()
            if g.hogar_id == hogar_id
        )
