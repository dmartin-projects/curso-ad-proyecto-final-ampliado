# informes/infrastructure/database/mappers/informe_mapper.py — fila → BO (módulo 88)
from core.domain.vo.mes import Mes
from informes.domain.bo.informe import Informe
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel


def informe_a_bo(fila: InformeMensualModel) -> Informe:
    return Informe(
        hogar_id=fila.hogar_id,
        mes=Mes.de(fila.mes),
        archivo=fila.archivo.name,
        tamano=fila.tamano,
        generado_por_id=fila.generado_por_id,
        id=fila.pk,
    )
