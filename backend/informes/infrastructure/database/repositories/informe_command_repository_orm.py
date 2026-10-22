# informes/infrastructure/database/repositories/informe_command_repository_orm.py — IInformeCommandRepository con el ORM (módulo 88)
from django.core.files.base import ContentFile

from core.domain.vo.mes import Mes
from informes.domain.bo.informe import Informe
from informes.domain.repositories.i_informe_command_repository import IInformeCommandRepository
from informes.infrastructure.database.mappers.informe_mapper import informe_a_bo
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel


class InformeCommandRepositoryORM(IInformeCommandRepository):
    def del_mes(self, hogar_id: int, mes: Mes) -> Informe | None:
        fila = InformeMensualModel.objects.select_for_update().filter(hogar_id=hogar_id, mes=mes.inicio).first()
        if fila is None:
            return None
        return informe_a_bo(fila)

    def guardar(self, informe: Informe, pdf: bytes) -> str | None:
        fila = InformeMensualModel.objects.filter(pk=informe.id).first() or InformeMensualModel(
            hogar_id=informe.hogar_id, mes=informe.mes.inicio
        )
        anterior = fila.archivo.name or None
        fila.generado_por_id, fila.tamano = informe.generado_por_id, informe.tamano
        fila.archivo.save("informe.pdf", ContentFile(pdf), save=False)  # ruta_informe: un nombre nuevo cada vez
        fila.save()
        informe.id, informe.archivo = fila.pk, fila.archivo.name
        return anterior
