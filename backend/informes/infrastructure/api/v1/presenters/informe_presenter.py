# informes/infrastructure/api/v1/presenters/informe_presenter.py — del OutputDTO a lo que lee el serializer (módulo 88)
from types import SimpleNamespace

from informes.application.shared.dtos.informe_listado_output_dto import InformeListadoOutputDTO


def presentar(i: InformeListadoOutputDTO) -> SimpleNamespace:
    """InformeSerializer calcula `automatico` desde generado_por_id (como con el modelo)."""
    return SimpleNamespace(
        pk=i.id,
        id=i.id,
        mes=i.mes,
        tamano=i.tamano,
        generado_por_id=i.generado_por_id,
        creado=i.creado,
        actualizado=i.actualizado,
    )
