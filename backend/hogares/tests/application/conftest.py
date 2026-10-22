import pytest

from hogares.tests.fakes.mundo import ANA, LUIS, Mundo


@pytest.fixture
def mundo():
    """Los use cases de hogares montados con fakes: sin base de datos, en milisegundos (módulo 88)."""
    return Mundo(emails={ANA: "ana@example.com", LUIS: "luis@example.com"})
