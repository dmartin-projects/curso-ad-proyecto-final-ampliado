# asistente/infrastructure/database/repositories/grafico_fijado_query_service_orm.py (módulo 97)
from asistente.domain.read_models.grafico_fijado_listado import GraficoFijadoListado
from asistente.domain.repositories.i_grafico_fijado_query_service import IGraficoFijadoQueryService
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico
from asistente.infrastructure.database.models.grafico_fijado_model import GraficoFijado as GraficoFijadoModel


class GraficoFijadoQueryServiceORM(IGraficoFijadoQueryService):
    def listar(self, hogar_id):
        filas = GraficoFijadoModel.objects.filter(hogar_id=hogar_id).select_related("usuario").order_by("creado", "id")
        return tuple(
            GraficoFijadoListado(
                f.pk,
                EspecificacionDeGrafico(f.tipo, f.titulo, f.fuente, f.argumentos),
                (f.usuario.nombre or "") if f.usuario else "",
                f.creado,
            )
            for f in filas
        )
