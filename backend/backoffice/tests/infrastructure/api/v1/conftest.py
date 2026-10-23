import pytest
from django.contrib.auth.models import Group

from conftest import CuentaFactory, HogarFactory, UsuarioFactory
from tickets.models import Ticket
from tickets.tests.conftest import archivo_ticket

URL = "/api/v1/backoffice/"


@pytest.fixture
def soporte(sesion_con_mfa):
    usuario = UsuarioFactory(is_staff=True)
    usuario.groups.add(
        Group.objects.get(name="Soporte")
    )  # lo crea post_migrate (core/infrastructure/database/grupos.py)
    c = sesion_con_mfa(usuario)  # módulo 92, ejercicio 1: el personal, con dos factores
    c.usuario = usuario
    return c


@pytest.fixture
def superusuario(sesion_con_mfa):
    return sesion_con_mfa(UsuarioFactory(is_staff=True, is_superuser=True))


def ticket(hogar=None, estado=Ticket.Estado.ERROR, huella="a", **extra):
    hogar = hogar or HogarFactory()
    return Ticket.objects.create(
        hogar=hogar,
        cuenta=CuentaFactory(hogar=hogar),
        archivo=archivo_ticket(),
        huella_archivo=huella,
        estado=estado,
        **extra,
    )
