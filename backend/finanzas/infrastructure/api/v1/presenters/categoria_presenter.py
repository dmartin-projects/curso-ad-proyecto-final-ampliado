# finanzas/infrastructure/api/v1/presenters/categoria_presenter.py — del OutputDTO a lo que lee el serializer (módulo 87)
from types import SimpleNamespace

from finanzas.application.shared.dtos.categoria_listada_output_dto import CategoriaListadaOutputDTO


def presentar(c: CategoriaListadaOutputDTO) -> SimpleNamespace:
    return SimpleNamespace(
        id=c.id,
        nombre=c.nombre,
        padre=SimpleNamespace(pk=c.padre_id) if c.padre_id is not None else None,  # PrimaryKeyRelatedField lee .pk
        color=c.color,
        icono=c.icono,
        orden=c.orden,
        es_ingreso=c.es_ingreso,
    )
