"""Domain service: reordenar las categorías de un hogar (módulo 87)."""

from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.services.reordenar_categorias import reordenar


def test_reordenar_ignora_lo_que_no_es_del_hogar():
    a, b = Categoria(hogar_id=1, nombre="A", id=1), Categoria(hogar_id=1, nombre="B", id=2)
    assert [(c.id, c.orden) for c in reordenar([a, b], [2, 99, 1])] == [(2, 0), (1, 2)]
