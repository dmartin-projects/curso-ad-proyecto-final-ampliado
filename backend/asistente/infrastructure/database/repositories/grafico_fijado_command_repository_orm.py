# asistente/infrastructure/database/repositories/grafico_fijado_command_repository_orm.py (módulo 97)
from asistente.domain.bo.grafico_fijado import GraficoFijado
from asistente.domain.exceptions.grafico_no_encontrado_exception import GraficoNoEncontradoException
from asistente.domain.repositories.i_grafico_fijado_command_repository import IGraficoFijadoCommandRepository
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico
from asistente.infrastructure.database.models.grafico_fijado_model import GraficoFijado as GraficoFijadoModel
from core.infrastructure.database.guardado import guardar_fila


class GraficoFijadoCommandRepositoryORM(IGraficoFijadoCommandRepository):
    def obtener(self, hogar_id, grafico_id):
        f = GraficoFijadoModel.objects.filter(pk=grafico_id, hogar_id=hogar_id).first()
        if f is None:
            raise GraficoNoEncontradoException()
        return GraficoFijado(
            f.hogar_id, f.usuario_id, EspecificacionDeGrafico(f.tipo, f.titulo, f.fuente, f.argumentos), id=f.pk
        )

    def guardar(self, grafico):
        e = grafico.especificacion
        fila = GraficoFijadoModel(
            pk=grafico.id,
            hogar_id=grafico.hogar_id,
            usuario_id=grafico.usuario_id,
            tipo=str(e.tipo),
            titulo=e.titulo,
            fuente=e.fuente,
            argumentos=dict(e.argumentos),
        )
        guardar_fila(fila, ["tipo", "titulo", "fuente", "argumentos"], {})
        grafico.id = fila.pk

    def eliminar(self, grafico):
        GraficoFijadoModel.objects.filter(pk=grafico.id).delete()
