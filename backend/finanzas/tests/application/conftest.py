import pytest

from finanzas.tests.fakes.mundo import Mundo


@pytest.fixture
def mundo():
    """Los use cases montados con fakes: sin base de datos, sin HTTP, en milisegundos (módulo 87)."""
    return Mundo()
