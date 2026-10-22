"""Lógica pura de reconocer comercios (módulos 72 y 87): no necesita la base de datos."""

import pytest

from finanzas.domain.services.normalizacion import normalizar


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("MERCADONA, S.A. 1234 MADRID", "mercadona madrid"),
        ("Compra tarj. *4321 LIDL SUPERMERCADOS", "lidl supermercados"),
        ("Farmacia Ñandú", "farmacia nandu"),
    ],
)
def test_normalizar(texto, esperado):
    assert normalizar(texto) == esperado
