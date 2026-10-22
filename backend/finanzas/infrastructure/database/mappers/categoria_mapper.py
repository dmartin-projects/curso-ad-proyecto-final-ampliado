# finanzas/infrastructure/database/mappers/categoria_mapper.py — BO ↔ fila (módulo 87)
from finanzas.domain.bo.categoria import Categoria
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel


def categoria_a_bo(fila: CategoriaModel) -> Categoria:
    return Categoria(
        id=fila.pk,
        hogar_id=fila.hogar_id,
        nombre=fila.nombre,
        padre_id=fila.padre_id,
        color=fila.color,
        icono=fila.icono,
        orden=fila.orden,
        es_ingreso=fila.es_ingreso,
    )


def categoria_a_modelo(c: Categoria) -> CategoriaModel:
    return CategoriaModel(
        pk=c.id,
        hogar_id=c.hogar_id,
        nombre=c.nombre,
        padre_id=c.padre_id,
        color=c.color,
        icono=c.icono,
        orden=c.orden,
        es_ingreso=c.es_ingreso,
    )
