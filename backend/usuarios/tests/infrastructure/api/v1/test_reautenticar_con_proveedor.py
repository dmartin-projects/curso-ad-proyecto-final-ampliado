"""Módulo 92, ejercicio 3: el step-up de una cuenta sin contraseña, con su proveedor (max_age=0 y auth_time)."""

import json
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from django.test import Client
from rest_framework.test import APIClient

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container
from usuarios.models import IdentidadExterna
from usuarios.tests.infrastructure.api.v1.test_social_api import SPA, S, destino, login_google, vuelta
from usuarios.tests.infrastructure.ayudas_mfa import A

pytestmark = pytest.mark.django_db


@pytest.fixture
def ana(proveedores, time_machine):
    """Creada con Google (sin contraseña), con su sesión de la SPA abierta hace 6 minutos: ya no es "reciente"."""
    login_google(Client(), proveedores.google, sub="sub-ana")
    usuario = IdentidadExterna.objects.get(sub="sub-ana").usuario
    sesion = container.iniciar_sesion().ejecutar(IniciarSesionInputDTO(usuario.pk, Factor.PROVEEDOR))
    spa = APIClient()
    spa.credentials(HTTP_AUTHORIZATION=f"Bearer {sesion.tokens.access}")
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=6))
    return spa


def ida(spa, proveedor="google"):
    r = spa.post(S + f"{proveedor}/reautenticar/", {"volver": "/seguridad"})
    navegador = Client()
    navegador.cookies[f"social_{proveedor}"] = r.cookies[f"social_{proveedor}"].value  # el navegador de la SPA
    return r.json()["url"], navegador


def test_sin_contrasena_se_confirma_con_el_proveedor_y_la_accion_se_puede_hacer(ana, proveedores):
    assert ana.post(A + "seguridad/totp/").status_code == 401  # una acción sensible: hace falta el step-up
    assert ana.get(A + "reautenticar/").json() == {"factores": [], "proveedores": ["google"], "max_age": 300}
    url, navegador = ida(ana)
    peticion = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
    assert peticion["max_age"] == "0"  # que vuelva a pedir la contraseña…
    assert json.loads(peticion["claims"]) == {"id_token": {"auth_time": {"essential": True}}}  # …y diga cuándo
    datos = proveedores.google.autorizar(url, sub="sub-ana", auth_time=int(time.time()))
    assert destino(vuelta(navegador, "google", datos)) == (f"{SPA}/seguridad", {"reautenticada": "google"})
    assert ana.post(A + "seguridad/totp/").status_code == 200  # ya es reciente


@pytest.mark.parametrize("auth_time", [None, "hace una hora"])
def test_si_el_proveedor_no_vuelve_a_autenticar_no_vale(ana, proveedores, auth_time):
    url, navegador = ida(ana)
    claims = {} if auth_time is None else {"auth_time": int(time.time()) - 3600}  # su sesión de Google, sin más
    r = vuelta(navegador, "google", proveedores.google.autorizar(url, sub="sub-ana", **claims))
    assert destino(r) == (
        f"{SPA}/seguridad", {"error_social": "reautenticacion_no_reciente", "proveedor": "google"}
    )  # fmt: skip
    assert ana.post(A + "seguridad/totp/").status_code == 401


def test_el_google_de_otra_persona_no_confirma_nada(ana, proveedores):
    url, navegador = ida(ana)
    datos = proveedores.google.autorizar(url, sub="sub-de-otro", auth_time=int(time.time()))
    assert destino(vuelta(navegador, "google", datos))[1]["error_social"] == "identidad_de_otra_cuenta"


def test_github_no_dice_cuando_se_autentico(ana):
    r = ana.post(S + "github/reautenticar/", {"volver": "/seguridad"})
    assert (r.status_code, r.json()["type"]) == (404, "proveedor_no_disponible")
