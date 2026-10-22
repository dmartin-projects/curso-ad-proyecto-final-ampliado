"""Reglas de los hogares vistas desde la API (módulo 88): las del dominio llegan como problem details."""

import pytest

from conftest import CuentaFactory
from eventos.domain.services.mensajes import MEMBRESIAS, MOVIMIENTOS
from eventos.models import EventoPendiente
from hogares.models import Membresia

pytestmark = pytest.mark.django_db
URL = "/api/v1/hogares/"


def test_el_ultimo_admin_no_puede_expulsarse(cliente, hogar_con_roles):
    hogar, roles = hogar_con_roles
    c = cliente(roles["admin"])
    yo = Membresia.objects.get(hogar=hogar, usuario=roles["admin"])
    r = c.delete(f"{URL}{hogar.pk}/miembros/{yo.pk}/")
    assert r.status_code == 409 and r.json()["type"] == "ultimo_administrador"
    lector = Membresia.objects.get(hogar=hogar, usuario=roles["lector"])
    assert c.delete(f"{URL}{hogar.pk}/miembros/{lector.pk}/").status_code == 204


def test_una_zona_horaria_que_no_existe_es_un_400_y_no_un_dashboard_roto(cliente, hogar_con_roles):
    hogar, roles = hogar_con_roles
    c = cliente(roles["admin"])
    r = c.patch(f"{URL}{hogar.pk}/", {"zona_horaria": "Europa/Madrid"})
    assert r.status_code == 400 and "zona_horaria" in r.json()["errors"]
    assert c.get(f"{URL}{hogar.pk}/dashboard/").status_code == 200  # el dashboard sigue funcionando
    assert c.patch(f"{URL}{hogar.pk}/", {"zona_horaria": "Atlantic/Canary"}).status_code == 200


def test_borrar_un_hogar_deja_un_tombstone_por_movimiento_y_membresia(cliente, hogar_con_roles):
    # La cascada no pasa por ningún use case: la cubren los receivers de cascada de eventos (módulo 88)
    hogar, roles = hogar_con_roles
    c = cliente(roles["admin"])
    cuenta = CuentaFactory(hogar=hogar)
    ids = {
        c.post(
            f"{URL}{hogar.pk}/movimientos/",
            {"fecha": "2026-10-01", "importe": "-5", "concepto": "Pan", "cuenta": cuenta.pk},
        ).json()["id"]  # fmt: skip
        for _ in range(2)
    }
    EventoPendiente.objects.all().delete()
    assert c.delete(f"{URL}{hogar.pk}/").status_code == 204
    tombstones = EventoPendiente.objects.filter(valor__isnull=True)
    assert {int(e.clave) for e in tombstones.filter(topic=MOVIMIENTOS)} == ids
    assert {e.clave for e in tombstones.filter(topic=MEMBRESIAS)} == {f"{hogar.pk}:{u.pk}" for u in roles.values()} - {
        f"{hogar.pk}:{roles['ajeno'].pk}"
    }


def test_borrar_un_hogar_con_importaciones_y_tickets(cliente, hogar_con_roles):
    # Importacion.cuenta y Ticket.cuenta son RESTRICT: borrar el hogar entero sí puede (y no da un 500).
    # Aquí y no en los tests de importaciones o de tickets: esas apps no se conocen entre sí (import-linter)
    from importaciones.models import Importacion
    from tickets.models import Ticket

    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    Importacion.objects.create(
        hogar=hogar, cuenta=cuenta, archivo="importaciones/x.csv", nombre_original="x.csv", formato="csv"
    )
    Ticket.objects.create(
        hogar=hogar, cuenta=cuenta, archivo="tickets/x.jpg", nombre_original="x.jpg", tipo="image/jpeg"
    )
    assert cliente(roles["admin"]).delete(f"{URL}{hogar.pk}/").status_code == 204
    assert not Importacion.objects.filter(hogar=hogar).exists() and not Ticket.objects.filter(hogar=hogar).exists()


def test_salir_de_un_hogar(cliente, hogar_con_roles):  # ejercicio 1
    hogar, roles = hogar_con_roles
    assert cliente(roles["lector"]).post(f"{URL}{hogar.pk}/miembros/salir/").status_code == 204
    assert not Membresia.objects.filter(hogar=hogar, usuario=roles["lector"]).exists()
    r = cliente(roles["admin"]).post(f"{URL}{hogar.pk}/miembros/salir/")
    assert r.status_code == 409 and r.json()["type"] == "ultimo_administrador"


def test_expulsar_queda_auditado(cliente, hogar_con_roles):  # ejercicio 3
    from core.models import RegistroAuditoria

    hogar, roles = hogar_con_roles
    lector = Membresia.objects.get(hogar=hogar, usuario=roles["lector"])
    assert cliente(roles["admin"]).delete(f"{URL}{hogar.pk}/miembros/{lector.pk}/").status_code == 204
    r = RegistroAuditoria.objects.get(object_id=str(lector.pk), content_type__model="membresia")
    assert (r.accion, r.usuario_id) == ("borrar", roles["admin"].pk)
