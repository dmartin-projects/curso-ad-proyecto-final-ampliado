# backoffice/infrastructure/database/repositories/auditoria_soporte_query_service_orm.py — IAuditoriaSoporteQueryService con el ORM (módulo 88)
from backoffice.domain.read_models.registro_auditoria_soporte import RegistroAuditoriaSoporte
from backoffice.domain.repositories.i_auditoria_soporte_query_service import IAuditoriaSoporteQueryService
from backoffice.infrastructure.database.repositories.listados import listar
from core.models import RegistroAuditoria as RegistroAuditoriaModel

BUSQUEDA = ("representacion", "usuario__email")


def _a_read_model(r: RegistroAuditoriaModel) -> RegistroAuditoriaSoporte:
    return RegistroAuditoriaSoporte(
        id=r.pk,
        fecha=r.fecha,
        usuario_email=None if r.usuario is None else r.usuario.email,
        accion=r.accion,
        modelo=f"{r.content_type.app_label}.{r.content_type.model}",
        object_id=r.object_id,
        representacion=r.representacion,
        cambios=r.cambios,
    )


class AuditoriaSoporteQueryServiceORM(IAuditoriaSoporteQueryService):
    @staticmethod
    def _todos():
        return RegistroAuditoriaModel.objects.select_related("usuario", "content_type")

    def listar(self, query, *, modelo=None):
        qs = self._todos()
        if modelo:
            app, _, nombre = modelo.partition(".")
            qs = qs.filter(content_type__app_label=app, content_type__model=nombre)
        return listar(qs, query, BUSQUEDA, _a_read_model)

    def detalle(self, registro_id):
        fila = self._todos().filter(pk=registro_id).first()
        return None if fila is None else _a_read_model(fila)
