"""Contract test del repositorio de informes (módulo 88): el del ORM y el de memoria."""

import pytest

from conftest import HogarFactory
from core.domain.vo.mes import Mes
from informes.domain.bo.informe import Informe
from informes.infrastructure.database.repositories.informe_command_repository_orm import InformeCommandRepositoryORM
from informes.tests.fakes.informe_command_repository_fake import InformeCommandRepositoryFake


@pytest.fixture(params=["memoria", "orm"])
def entorno(request):
    if request.param == "memoria":
        return InformeCommandRepositoryFake(), 1
    request.getfixturevalue("db")
    return InformeCommandRepositoryORM(), HogarFactory().pk


def test_uno_por_hogar_y_mes(entorno):
    repo, hogar = entorno
    assert repo.del_mes(hogar, Mes(2026, 10)) is None
    nuevo = Informe(hogar, Mes(2026, 10), tamano=3)
    assert repo.guardar(nuevo, b"pdf") is None and nuevo.id and nuevo.archivo
    leido = repo.del_mes(hogar, Mes(2026, 10))
    assert (leido.id, leido.tamano, leido.archivo) == (nuevo.id, 3, nuevo.archivo)
    assert repo.guardar(leido, b"otro") == nuevo.archivo  # el viejo, para borrarlo al confirmar
    assert repo.del_mes(hogar, Mes(2026, 9)) is None
