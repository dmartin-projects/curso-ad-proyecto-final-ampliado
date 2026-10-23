"""Desde dónde entra alguien (módulo 92), sin base de datos."""

import pytest

from usuarios.domain.services.dispositivos import describir_dispositivo, es_dispositivo_nuevo, ip_aproximada


@pytest.mark.parametrize(
    ("ua", "descripcion"),
    [
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141.0 Safari/537.36", "Chrome en macOS"),
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 Version/18.6 Safari/604.1", "Safari en iOS"),
        ("Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 Chrome/141.0 Mobile Safari/537.36", "Chrome en Android"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/141.0 Safari/537.36 Edg/141.0", "Edge en Windows"),
        ("Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0", "Firefox en Linux"),
        ("curl/8.5.0", "Navegador"),
    ],
)  # fmt: skip
def test_describir_el_dispositivo(ua, descripcion):
    assert describir_dispositivo(ua) == descripcion


def test_la_ip_aproximada_es_la_red():
    assert ip_aproximada("83.45.120.17") == "83.45.120.0/24"
    assert ip_aproximada("2a02:9130:84a1:3c00::1") == "2a02:9130:84a1::/48"
    assert ip_aproximada("no es una ip") == ""


def test_dispositivo_nuevo():
    assert es_dispositivo_nuevo(conocido=False, sesiones_anteriores=3)
    assert not es_dispositivo_nuevo(conocido=True, sesiones_anteriores=3)
    assert not es_dispositivo_nuevo(conocido=False, sesiones_anteriores=0)  # la primera vez en su cuenta nueva
