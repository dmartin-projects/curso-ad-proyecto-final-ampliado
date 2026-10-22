"""La API de los informes (módulos 78 y 88)."""

from datetime import date

import pytest
from django.core import mail

pytestmark = pytest.mark.django_db
OCT = date(2026, 10, 1)


def test_api_generar_listar_y_descargar(hogar_con_datos, cliente, django_capture_on_commit_callbacks):
    hogar, roles = hogar_con_datos
    base = f"/api/v1/hogares/{hogar.pk}/informes/"

    assert cliente(roles["lector"]).post(base, {"mes": "2026-10"}).status_code == 403
    assert cliente(roles["miembro"]).post(base, {"mes": "2999-01"}).status_code == 400
    with django_capture_on_commit_callbacks(execute=True):
        r = cliente(roles["miembro"]).post(base, {"mes": "2026-10"})
    assert r.status_code == 202 and r.data == {"mes": "2026-10", "estado": "generando"}
    assert len(mail.outbox) == 0  # bajo demanda no se envía salvo que se pida

    lector = cliente(roles["lector"])
    assert [i["mes"] for i in lector.get(base).data] == ["2026-10"]
    assert lector.get(base + "2026-10/").data["automatico"] is False
    r = lector.get(base + "2026-10/pdf/")
    assert r.status_code == 200 and r["Content-Type"] == "application/pdf"
    assert r["Content-Disposition"] == 'attachment; filename="gastos-Piso Ruzafa-2026-10.pdf"'
    assert b"".join(r.streaming_content).startswith(b"%PDF-")
    assert lector.get(base + "2026-09/pdf/").status_code == 404
    assert lector.get(base + "2026-13/pdf/").status_code == 404
    assert cliente(roles["ajeno"]).get(base).status_code == 404
