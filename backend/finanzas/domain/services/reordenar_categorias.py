# finanzas/domain/services/reordenar_categorias.py — domain service: no es de UNA categoría (módulo 87)
from finanzas.domain.bo.categoria import Categoria


def reordenar(categorias: list[Categoria], ids: list[int]) -> list[Categoria]:
    """El orden de la lista `ids` pasa a ser el de las categorías. Los ids que no están (de otro hogar), fuera."""
    por_id = {c.id: c for c in categorias}
    for orden, categoria_id in enumerate(ids):
        if categoria_id in por_id:
            por_id[categoria_id].orden = orden
    return [por_id[i] for i in ids if i in por_id]
