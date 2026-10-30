import pytest

from asistente.tests.fakes.mundo import Mundo


@pytest.fixture
def mundo():
    return Mundo()
