"""Solo el personal, con el permiso de su grupo (módulos 79 y 88) y una sesión de dos factores (módulo 92, ej. 1)."""

import time

import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from backoffice.tests.infrastructure.api.v1.conftest import URL
from conftest import MembresiaFactory, UsuarioFactory
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container
from usuarios.models import IdentidadExterna
from usuarios.tests.infrastructure.api.v1.test_reautenticar_con_proveedor import ida
from usuarios.tests.infrastructure.api.v1.test_social_api import vuelta as vuelta_social
from usuarios.tests.infrastructure.ayudas_mfa import PASSWORD
from usuarios.tests.infrastructure.conftest import proveedores  # noqa: F401 (el fixture de los proveedores falsos)

pytestmark = pytest.mark.django_db


def test_quien_no_es_personal_ni_sabe_que_existe(cliente, api):
    usuario = MembresiaFactory().usuario  # usuario normal, admin de su hogar
    assert cliente(usuario).get(URL + "tickets/").status_code == 404
    assert api.get(URL + "tickets/").status_code == 401


def test_personal_sin_el_permiso_concreto_recibe_403(sesion_con_mfa):
    sin_grupo = sesion_con_mfa(UsuarioFactory(is_staff=True))
    assert sin_grupo.get(URL + "tickets/").status_code == 403


# ── Módulo 92, ejercicio 1: el backoffice exige una sesión de dos factores ──


def test_el_personal_sin_mfa_no_entra_en_el_backoffice(sesion):
    usuario = UsuarioFactory(is_staff=True)
    usuario.groups.add(Group.objects.get(name="Soporte"))
    r = sesion(usuario).get(URL + "resumen/")
    assert (r.status_code, r.json()["type"]) == (403, "mfa_requerido")


def test_una_sesion_de_un_factor_sube_de_nivel_con_un_step_up(sesion):
    from usuarios.tests.infrastructure.ayudas_mfa import activar_mfa, codigo

    usuario = UsuarioFactory(is_staff=True)
    usuario.groups.add(Group.objects.get(name="Soporte"))
    c = sesion(usuario)  # entró con la contraseña…
    secreto, _ = activar_mfa(usuario)  # …y activó el MFA después: esta sesión sigue siendo de un factor
    assert c.get(URL + "resumen/").status_code == 403
    assert c.post("/api/v1/auth/reautenticar/", {"factor": "totp", "codigo": codigo(secreto)}).status_code == 204
    assert c.get(URL + "resumen/").status_code == 200


def personal_con_google():
    usuario = UsuarioFactory(is_staff=True, email="soporte@example.com")
    usuario.groups.add(Group.objects.get(name="Soporte"))
    IdentidadExterna.objects.create(usuario=usuario, proveedor="google", sub="sub-soporte", email="soporte@gmail.com")
    return usuario


def test_proveedor_y_luego_la_contrasena_no_son_dos_factores():
    """Entrar con Google y confirmar con la contraseña: dos veces "una contraseña" (la de Google y la de Gastos), y el
    MFA del proveedor no cuenta. La sesión sigue siendo de un factor: sin MFA activo, el backoffice no se abre."""
    usuario = personal_con_google()
    abierta = container.iniciar_sesion().ejecutar(IniciarSesionInputDTO(usuario.pk, Factor.PROVEEDOR))
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {abierta.tokens.access}")
    assert c.post("/api/v1/auth/reautenticar/", {"factor": "contrasena", "codigo": PASSWORD}).status_code == 204
    r = c.get(URL + "resumen/")
    assert (r.status_code, r.json()["type"]) == (403, "mfa_requerido")


def test_la_contrasena_y_luego_el_proveedor_no_son_dos_factores(sesion, request):
    """Y al revés: entrar con la contraseña y confirmar con Google (ejercicio 3)."""
    google = request.getfixturevalue("proveedores").google
    usuario = personal_con_google()
    c = sesion(usuario)
    url, navegador = ida(c)
    datos = google.autorizar(url, sub="sub-soporte", auth_time=int(time.time()))
    assert vuelta_social(navegador, "google", datos).status_code == 302
    r = c.get(URL + "resumen/")
    assert (r.status_code, r.json()["type"]) == (403, "mfa_requerido")
