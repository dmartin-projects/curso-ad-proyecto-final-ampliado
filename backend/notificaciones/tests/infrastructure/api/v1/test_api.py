"""La API de las notificaciones (módulos 76 y 88)."""

import pytest

from conftest import UsuarioFactory
from notificaciones.models import Notificacion

pytestmark = pytest.mark.django_db
T = Notificacion.Tipo


def test_api_de_notificaciones(cliente):
    yo, otro = UsuarioFactory(), UsuarioFactory()
    mias = [Notificacion.objects.create(usuario=yo, tipo=T.TICKET_PROCESADO, titulo=f"n{i}") for i in range(3)]
    ajena = Notificacion.objects.create(usuario=otro, tipo=T.TICKET_PROCESADO, titulo="ajena")
    c = cliente(yo)

    assert [n["titulo"] for n in c.get("/api/v1/notificaciones/").data["results"]] == ["n2", "n1", "n0"]
    assert c.get("/api/v1/notificaciones/no-leidas/").data == {"no_leidas": 3}
    assert c.post(f"/api/v1/notificaciones/{mias[0].pk}/leer/").status_code == 204
    assert c.post(f"/api/v1/notificaciones/{ajena.pk}/leer/").status_code == 404
    assert c.get("/api/v1/notificaciones/", {"leida": "false"}).data["results"][-1]["titulo"] == "n1"
    assert c.post("/api/v1/notificaciones/leer-todas/", {}).data == {"actualizadas": 2}
    assert c.get("/api/v1/notificaciones/no-leidas/").data == {"no_leidas": 0}
    ajena.refresh_from_db()
    assert ajena.leida is False


def test_ticket_websocket_requiere_sesion(api, cliente):
    assert api.post("/api/v1/notificaciones/ws-ticket/").status_code == 401
    r = cliente(UsuarioFactory()).post("/api/v1/notificaciones/ws-ticket/")
    assert r.status_code == 201 and len(r.data["ticket"]) >= 40 and r.data["caduca_en"] == 30
