"""La auditoría, de solo lectura (módulos 79 y 88)."""

import pytest

from backoffice.tests.infrastructure.api.v1.conftest import URL, ticket

pytestmark = pytest.mark.django_db


def test_la_auditoria_es_de_solo_lectura(soporte):
    soporte.post(URL + "tickets/reprocesar/", {"ids": [ticket().pk]})
    lista = soporte.get(URL + "auditoria/", {"modelo": "tickets.ticket"}).data["results"]
    assert len(lista) == 1 and lista[0]["accion"] == "modificar"
    # DELETE no es una acción de la vista: PermisosPorAccion cierra por defecto (403) antes incluso del 405
    assert soporte.delete(URL + f"auditoria/{lista[0]['id']}/").status_code == 403
