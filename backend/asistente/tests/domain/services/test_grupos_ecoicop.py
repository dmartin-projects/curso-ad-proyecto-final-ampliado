"""Módulo 95: de una categoría de Gastos a su grupo del IPC. Explícito y probado: un error aquí compara peras con
manzanas sin que nadie lo note."""

import pytest

from asistente.domain.services.grupos_ecoicop import GENERAL, grupo_de
from finanzas.domain.services.categorias_por_defecto import CATEGORIAS_POR_DEFECTO


@pytest.mark.parametrize(
    "categoria, padre, codigo",
    [
        ("Supermercado", None, "CP011"),
        ("Restaurantes", None, "CP111"),
        ("Luz", "Hogar", "CP0451"),
        ("Combustible", "Transporte", "CP0722"),
        ("Internet y móvil", "Hogar", "CP083"),
        ("Alquiler / hipoteca", "Hogar", "CP041"),
        ("Farmacia", "Salud", "CP061"),
        ("Educación", None, "CP10"),
        ("EDUCACION", None, "CP10"),  # sin tildes ni mayúsculas: lo escribe cada hogar
        ("Casa", None, "CP04"),
        ("Mascotas", "Ocio", "CP09"),  # una subcategoría sin grupo: el de su principal
    ],
)
def test_grupos(categoria, padre, codigo):
    g = grupo_de(categoria, padre)
    assert (g.codigo, g.exacto) == (codigo, True)


def test_lo_que_no_tiene_grupo_es_el_ipc_general_y_se_dice():
    assert grupo_de("Regalos") == GENERAL
    assert (GENERAL.codigo, GENERAL.exacto) == ("TOTAL", False)


def test_todas_las_categorias_por_defecto_tienen_grupo_salvo_otros():
    sin_grupo = [
        nombre
        for raiz, _, _, hijas in CATEGORIAS_POR_DEFECTO
        for nombre, padre in [(raiz, None), *((h, raiz) for h in hijas)]
        if not grupo_de(nombre, padre).exacto
    ]
    assert sin_grupo == ["Otros"]
