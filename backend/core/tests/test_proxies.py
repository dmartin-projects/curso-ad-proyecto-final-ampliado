"""Módulo 86: Django detrás de DOS proxies, Vercel (el rewrite de /api) y Caddy (en la VM).

Lo que llega a Django, porque Caddy lo deja así (infra/Caddyfile):
- Host: el de la API (api.gastos.tudominio.com), no el de la web;
- X-Forwarded-Proto: https;
- X-Forwarded-For: UNA sola IP, la del navegador (la que dice Vercel, si la petición trae su secreto).
El navegador, en cambio, cree que habla con https://gastos.tudominio.com: la cookie es de ese host.
"""

import pytest
from django.core.cache import cache
from django.test import Client

from conftest import UsuarioFactory

API = "api.gastos.tudominio.com"
DETRAS_DE_CADDY = {"HTTP_HOST": API, "HTTP_X_FORWARDED_PROTO": "https", "HTTP_ORIGIN": "https://gastos.tudominio.com"}
pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def produccion(settings):
    """Lo que importa aquí de config/settings/prod.py."""
    settings.ALLOWED_HOSTS = [API]
    settings.SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    settings.SECURE_SSL_REDIRECT = True
    settings.JWT_REFRESH_COOKIE = {**settings.JWT_REFRESH_COOKIE, "secure": True}
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, "NUM_PROXIES": 1}
    cache.clear()  # el throttling cuenta en la caché


def login(c, ip, password="clave-segura-123", email="ana@example.com"):
    datos = {"email": email, "password": password}
    return c.post(
        "/api/v1/auth/login/", datos, content_type="application/json", HTTP_X_FORWARDED_FOR=ip, **DETRAS_DE_CADDY
    )


def test_la_cookie_de_refresh_sirve_a_traves_del_rewrite():
    UsuarioFactory(email="ana@example.com")
    c = Client(enforce_csrf_checks=True)  # como un navegador: sin saltarse la protección CSRF

    r = login(c, "203.0.113.7")
    assert r.status_code == 200 and r.wsgi_request.is_secure()  # https gracias a SECURE_PROXY_SSL_HEADER
    cookie = r.cookies["refresh"]
    assert cookie["domain"] == ""  # sin Domain: el navegador la guarda para el host que VE (el de Vercel)
    assert cookie["path"] == "/api/v1/auth/" and cookie["secure"] and cookie["httponly"]
    assert cookie["samesite"] == "Strict"  # la página y /api son el mismo sitio: viaja igual

    # F5: Angular pide un access nuevo solo con la cookie. Un Origin "ajeno" (Vercel) no molesta: CSRF no aplica
    r = c.post("/api/v1/auth/refresh/", **DETRAS_DE_CADDY)
    assert r.status_code == 200 and "access" in r.json()


def test_sin_x_forwarded_proto_django_cree_que_es_http():
    r = Client().get("/api/v1/auth/login/", HTTP_HOST=API)
    assert r.status_code == 301 and r["Location"].startswith("https://")  # SECURE_SSL_REDIRECT: bucle infinito


def test_el_host_de_vercel_no_es_un_host_de_django():
    # USE_X_FORWARDED_HOST sigue en False: Django valida el Host que pone el proxy (la API), no el de la web
    r = Client().post("/api/v1/auth/login/", HTTP_HOST="gastos.tudominio.com", HTTP_X_FORWARDED_PROTO="https")
    assert r.status_code == 400  # DisallowedHost


def test_el_throttling_cuenta_por_navegador_y_no_por_proxy():
    UsuarioFactory(email="ana@example.com")
    c = Client()
    for _ in range(5):  # login: 5 por minuto (DEFAULT_THROTTLE_RATES)
        assert login(c, "203.0.113.7", password="mal").status_code == 401
    assert login(c, "203.0.113.7", password="mal").status_code == 429
    # Otro navegador, mismo Vercel y mismo Caddy: con NUM_PROXIES mal puesto, este también recibiría 429
    assert login(c, "198.51.100.20", password="mal").status_code == 401
