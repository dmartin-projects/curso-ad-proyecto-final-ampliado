"""Domain service: las categorías con las que nace un hogar (módulo 87)."""

from finanzas.domain.services.categorias_por_defecto import por_defecto


def test_por_defecto():
    raices, hijas = por_defecto(hogar_id=1)
    assert len(raices) == 11 and sum(map(len, hijas.values())) == 11
    assert [h.nombre for h in hijas["Salud"]] == ["Farmacia"] and raices[-1].es_ingreso
