# informes/infrastructure/database/repositories/informe_query_service_orm.py — IInformeQueryService con el ORM (módulo 88)
from finanzas.models import Movimiento as MovimientoModel
from hogares.models import Hogar as HogarModel
from informes.domain.read_models.informe_listado import InformeListado
from informes.domain.repositories.i_informe_query_service import IInformeQueryService
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel


def _a_read_model(i: InformeMensualModel) -> InformeListado:
    return InformeListado(i.pk, i.mes, i.archivo.name, i.tamano, i.generado_por_id, i.creado, i.actualizado)


class InformeQueryServiceORM(IInformeQueryService):
    def listar(self, hogar_id):
        return [_a_read_model(i) for i in InformeMensualModel.objects.filter(hogar_id=hogar_id)]

    def detalle(self, hogar_id, mes):
        fila = InformeMensualModel.objects.filter(hogar_id=hogar_id, mes=mes.inicio).first()
        return None if fila is None else _a_read_model(fila)

    def hogares_sin_informe(self, mes):
        con_movimientos = MovimientoModel.objects.del_mes(mes.inicio).values("hogar_id").distinct()
        # si Beat se reinicia y la lanza dos veces, no se repite nada
        sin_informe = HogarModel.objects.filter(pk__in=con_movimientos).exclude(informes__mes=mes.inicio)
        return list(sin_informe.values_list("pk", flat=True))

    def destinatarios(self, informe_id):
        informe = InformeMensualModel.objects.get(pk=informe_id)
        return list(informe.hogar.membresias.filter(usuario__is_active=True).values_list("usuario_id", flat=True))
