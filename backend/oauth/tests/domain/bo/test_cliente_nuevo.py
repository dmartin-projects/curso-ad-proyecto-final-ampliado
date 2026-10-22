"""Las reglas de los clientes y los scopes (módulo 90), sin base de datos."""

import pytest

from core.domain.enums.rol import Rol
from oauth.domain.bo.cliente_nuevo import ClienteNuevo
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.domain.exceptions.client_id_no_valido_exception import ClientIdNoValidoException
from oauth.domain.exceptions.nombre_obligatorio_exception import NombreObligatorioException
from oauth.domain.exceptions.redirect_uri_no_valida_exception import RedirectUriNoValidaException
from oauth.domain.exceptions.scopes_no_validos_exception import ScopesNoValidosException
from oauth.domain.services.redirect_uris import validar_redirect_uri
from oauth.domain.services.scopes import techo

NATIVA, WEB, SERVICIO, DISPOSITIVO = TipoCliente.NATIVA, TipoCliente.WEB, TipoCliente.SERVICIO, TipoCliente.DISPOSITIVO


def cliente(tipo=NATIVA, scopes=("openid", "gastos:leer"), redirect_uris=("http://127.0.0.1/callback",), **otros):
    return ClienteNuevo(nombre=otros.pop("nombre", "CLI"), tipo=tipo, scopes=frozenset(scopes),
                        redirect_uris=redirect_uris, **otros)  # fmt: skip


@pytest.mark.parametrize(
    "uri",
    ["https://app.example.com/callback", "http://127.0.0.1/callback", "http://[::1]:8080/cb", "https://x.com/cb?a=1"],
)
def test_redirect_uris_validas(uri):
    assert validar_redirect_uri(uri) == uri


@pytest.mark.parametrize(
    "uri",
    [
        "http://localhost/callback",  # RFC 8252 §8.3: localhost puede no ser esta máquina
        "http://app.example.com/callback",  # el code viajaría sin cifrar
        "https://app.example.com/callback#fragmento",  # RFC 6749 §3.1.2
        "https://*.example.com/callback",  # sin comodines: comparación exacta
        "/callback",  # relativa
        "com.gastos.app:/callback",  # esquemas propios: no los usa ningún cliente de Gastos
        "javascript:alert(1)",
    ],
)
def test_redirect_uris_no_validas(uri):
    with pytest.raises(RedirectUriNoValidaException):
        validar_redirect_uri(uri)


def test_tipos():
    assert not NATIVA.confidencial and WEB.confidencial and SERVICIO.confidencial
    assert NATIVA.con_usuario and WEB.con_usuario and not SERVICIO.con_usuario


def test_un_cliente_con_usuario_solo_pide_scopes_del_usuario():
    cliente(scopes=("openid", "email", "profile", "gastos:leer", "gastos:escribir"))
    for scopes in [("openid", "operaciones:leer"), ("openid", "admin"), ()]:
        with pytest.raises(ScopesNoValidosException):
            cliente(scopes=scopes)


def test_un_servicio_no_tiene_usuario_ni_redirect():
    cliente(SERVICIO, scopes=("operaciones:leer",), redirect_uris=())
    with pytest.raises(ScopesNoValidosException):
        cliente(SERVICIO, scopes=("openid",), redirect_uris=())  # sin usuario no hay identidad que dar
    with pytest.raises(ScopesNoValidosException):
        cliente(SERVICIO, scopes=("gastos:leer",), redirect_uris=())  # ni en nombre de quién actuar
    with pytest.raises(RedirectUriNoValidaException):
        cliente(SERVICIO, scopes=("operaciones:leer",))


def test_un_cliente_con_usuario_necesita_redirect():
    with pytest.raises(RedirectUriNoValidaException):
        cliente(WEB, redirect_uris=())


def test_nombre_y_client_id():
    with pytest.raises(NombreObligatorioException):
        cliente(nombre="  ")
    with pytest.raises(ClientIdNoValidoException):
        cliente(client_id="con espacios")
    assert cliente(client_id="gastos-cli").client_id == "gastos-cli"


def test_el_techo_de_los_scopes():
    assert techo({"openid", "gastos:leer"}) == Rol.LECTOR
    assert techo({"gastos:leer", "gastos:escribir"}) == Rol.MIEMBRO
    assert techo({"openid", "email"}) is None
    assert techo({"operaciones:leer"}) is None


def test_un_dispositivo_es_publico_sin_redirect_y_solo_pide_la_api():  # ejercicio 3
    assert not DISPOSITIVO.confidencial and DISPOSITIVO.con_usuario and not DISPOSITIVO.con_redirect
    cliente(DISPOSITIVO, scopes=("gastos:leer", "gastos:escribir"), redirect_uris=())
    with pytest.raises(ScopesNoValidosException):
        cliente(DISPOSITIVO, scopes=("openid", "gastos:leer"), redirect_uris=())  # el device flow no da ID tokens
    with pytest.raises(RedirectUriNoValidaException):
        cliente(DISPOSITIVO, scopes=("gastos:leer",))
