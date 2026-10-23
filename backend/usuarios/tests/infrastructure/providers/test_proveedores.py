"""Los adapters de los proveedores (módulo 91) contra proveedores simulados con respx: cada comprobación, con su test.

Sin base de datos: un adapter solo habla con el proveedor y devuelve un PerfilExterno (o LoginSocialNoValidoException).
"""

import base64
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from joserfc import jwt
from joserfc.jwk import ECKey, RSAKey

from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial
from usuarios.infrastructure.providers.proveedores_configurados import ProveedoresConfigurados
from usuarios.tests.infrastructure.proveedor_falso import TOKEN_DEL_PROVEEDOR


def transaccion(proveedor=Proveedor.GOOGLE, nonce="nonce-1"):
    return TransaccionSocial(proveedor, "state-1", nonce, "v" * 64, Proposito.ENTRAR)


def query(url):
    return {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}


def b64(datos: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(datos).encode()).rstrip(b"=").decode()


def completar(proveedor: Proveedor, falso, t=None, **claims):
    """Todo el viaje: la URL de ida, el proveedor la "atiende" y el adapter completa con lo que vuelve."""
    adapter = ProveedoresConfigurados().de(proveedor)
    t = t or transaccion(proveedor)
    return adapter.completar(t, falso.autorizar(adapter.url_de_autorizacion(t), **claims))


# ── La ida ──


def test_google_pide_openid_con_pkce_nonce_y_la_vuelta_registrada(proveedores):
    url = ProveedoresConfigurados().de(Proveedor.GOOGLE).url_de_autorizacion(transaccion())
    assert url.startswith("https://accounts.google.example/authorize?")
    q = query(url)
    assert q == {
        "response_type": "code",
        "client_id": "gastos.apps.googleusercontent.example",
        "redirect_uri": "https://gastos.example/api/v1/auth/social/google/vuelta/",
        "scope": "openid email profile",
        "state": "state-1",
        "nonce": "nonce-1",
        "prompt": "select_account",
        "code_challenge": q["code_challenge"],
        "code_challenge_method": "S256",
    }
    assert len(q["code_challenge"]) == 43 and q["code_challenge"] != "v" * 64  # el hash, nunca el verifier


def test_apple_vuelve_por_post_y_sin_pkce_si_no_lo_anuncia(proveedores):
    q = query(ProveedoresConfigurados().de(Proveedor.APPLE).url_de_autorizacion(transaccion(Proveedor.APPLE)))
    assert q["response_mode"] == "form_post" and q["scope"] == "openid name email" and q["nonce"] == "nonce-1"
    assert "code_challenge" not in q


def test_github_es_oauth_sin_nonce_pero_con_pkce(proveedores):
    q = query(ProveedoresConfigurados().de(Proveedor.GITHUB).url_de_autorizacion(transaccion(Proveedor.GITHUB)))
    assert q["scope"] == "read:user user:email" and q["code_challenge_method"] == "S256" and "nonce" not in q
    assert q["redirect_uri"] == "https://gastos.example/api/v1/auth/social/github/vuelta/"


# ── La vuelta de un OpenID Provider: el canje y el ID token ──


def test_google_canjea_con_su_secreto_y_el_verifier(proveedores):
    perfil = completar(Proveedor.GOOGLE, proveedores.google)
    assert perfil == PerfilExterno(Proveedor.GOOGLE, "1081", "ana@gmail.com", True, "Ana", "García")
    canje = proveedores.google.canjes[0]
    assert canje["code_verifier"] == "v" * 64 and canje["redirect_uri"].endswith("/social/google/vuelta/")
    usuario, clave = base64.b64decode(canje["_autorizacion"].removeprefix("Basic ")).decode().split(":")
    assert (usuario, clave) == ("gastos.apps.googleusercontent.example", "secreto-google")  # client_secret_basic


def test_google_acepta_su_iss_sin_esquema(proveedores):
    proveedores.google.trampas = {"iss": "accounts.google.example"}
    assert completar(Proveedor.GOOGLE, proveedores.google).sub == "1081"


@pytest.mark.parametrize(
    "trampa",
    [
        pytest.param({"iss": "https://otro-emisor.example"}, id="iss de otro emisor"),
        pytest.param({"aud": "otra-aplicacion"}, id="aud de otra aplicación"),
        pytest.param(
            {"aud": "otra-aplicacion", "azp": "gastos.apps.googleusercontent.example"}, id="aud de otra con azp"
        ),
        pytest.param({"aud": ["otra-aplicacion", "gastos.apps.googleusercontent.example"]}, id="varios aud sin azp"),
        pytest.param({"exp": int(time.time()) - 120, "iat": int(time.time()) - 720}, id="caducado"),
        pytest.param({"exp": None}, id="sin exp"),
        pytest.param({"nonce": "nonce-de-otra-peticion"}, id="nonce de otra autenticación"),
        pytest.param({"nonce": None}, id="sin nonce"),
        pytest.param({"at_hash": "no-es-el-del-access-token"}, id="at_hash de otro access token"),
    ],
)
def test_un_id_token_que_no_cuadra_se_rechaza(proveedores, trampa):
    proveedores.google.trampas = trampa
    with pytest.raises(LoginSocialNoValidoException):
        completar(Proveedor.GOOGLE, proveedores.google)


def test_un_id_token_firmado_con_otra_clave_se_rechaza(proveedores):
    proveedores.google.firmar_con = RSAKey.generate_key(2048, parameters={"kid": "clave-1"})  # mismo kid, otra clave
    with pytest.raises(LoginSocialNoValidoException):
        completar(Proveedor.GOOGLE, proveedores.google)


def test_alg_none_y_hs256_con_la_clave_publica_se_rechazan(proveedores):
    adapter = ProveedoresConfigurados().de(Proveedor.GOOGLE)
    falso = proveedores.google
    ahora = int(time.time())
    claims = {"iss": falso.emisor, "aud": falso.client_id, "sub": "1081", "iat": ahora, "exp": ahora + 600,
              "nonce": "nonce-1"}  # fmt: skip
    sin_firma = f"{b64({'alg': 'none', 'kid': 'clave-1'})}.{b64(claims)}."
    # HS256 con la clave PÚBLICA (la del JWKS, que tiene cualquiera) como secreto: la confusión de algoritmos.
    # A mano: joserfc ni siquiera deja construir esa clave
    firmado = f"{b64({'alg': 'HS256', 'kid': 'clave-1'})}.{b64(claims)}"
    mac = hmac.new(falso.clave.as_pem(private=False), firmado.encode(), hashlib.sha256).digest()
    hs256 = f"{firmado}.{base64.urlsafe_b64encode(mac).rstrip(b'=').decode()}"
    for token in (sin_firma, hs256):
        with pytest.raises(LoginSocialNoValidoException):
            adapter.validar_id_token(token, "nonce-1")
    assert adapter.validar_id_token(falso.id_token(sub="1081", nonce="nonce-1"), "nonce-1")["sub"] == "1081"


def test_si_el_proveedor_rota_la_clave_se_pide_el_jwks_otra_vez_una_sola_vez(proveedores):
    falso = proveedores.google
    assert completar(Proveedor.GOOGLE, falso).sub == "1081"  # el JWKS, en la caché
    falso.clave = RSAKey.generate_key(2048, parameters={"kid": "clave-2", "use": "sig"})
    falso.claves, falso.cabecera = [falso.claves[0], falso.clave], {"kid": "clave-2"}
    assert completar(Proveedor.GOOGLE, falso).sub == "1081"
    assert falso.jwks.call_count == 2
    falso.cabecera = {"kid": "inventado"}
    with pytest.raises(LoginSocialNoValidoException):  # un kid que no existe: UNA petición más, no un bucle
        completar(Proveedor.GOOGLE, falso)
    assert falso.jwks.call_count == 3


def test_sin_id_token_no_hay_login(proveedores):
    """Un access token solo no dice quién es la persona (OAuth no es autenticación): sin ID token, nada."""
    proveedores.google.token.mock(
        return_value=httpx.Response(200, json={"access_token": TOKEN_DEL_PROVEEDOR, "token_type": "Bearer"})
    )
    with pytest.raises(LoginSocialNoValidoException):
        completar(Proveedor.GOOGLE, proveedores.google)


def test_un_code_que_el_proveedor_rechaza(proveedores):
    adapter = ProveedoresConfigurados().de(Proveedor.GOOGLE)
    adapter.url_de_autorizacion(transaccion())
    with pytest.raises(LoginSocialNoValidoException):
        adapter.completar(transaccion(), {"code": "inventado", "state": "state-1"})
    with pytest.raises(LoginSocialNoValidoException):
        adapter.completar(transaccion(), {"state": "state-1"})  # sin code


def test_pkce_un_verifier_distinto_no_canjea(proveedores):
    adapter = ProveedoresConfigurados().de(Proveedor.GOOGLE)
    vuelta = proveedores.google.autorizar(adapter.url_de_autorizacion(transaccion()))
    otra = TransaccionSocial(Proveedor.GOOGLE, "state-1", "nonce-1", "w" * 64, Proposito.ENTRAR)
    with pytest.raises(LoginSocialNoValidoException):  # (lo que haría quien intercepta el code: no tiene el verifier)
        adapter.completar(otra, vuelta)


def test_el_discovery_de_otro_emisor_no_se_usa(proveedores):
    proveedores.google.metadatos = proveedores.google.metadatos | {"issuer": "https://otro.example"}
    with pytest.raises(LoginSocialNoValidoException):
        ProveedoresConfigurados().de(Proveedor.GOOGLE).url_de_autorizacion(transaccion())


def test_iss_en_la_vuelta_tiene_que_ser_el_suyo(proveedores):
    adapter = ProveedoresConfigurados().de(Proveedor.GOOGLE)
    vuelta = proveedores.google.autorizar(adapter.url_de_autorizacion(transaccion()))
    with pytest.raises(LoginSocialNoValidoException):  # RFC 9207 (mix-up): la respuesta dice venir de otro
        adapter.completar(transaccion(), vuelta | {"iss": "https://otro.example"})
    assert proveedores.google.canjes == []  # y no se llega a canjear


def test_si_el_proveedor_no_responde(proveedores):
    proveedores.http.get("https://accounts.google.example/.well-known/openid-configuration").mock(
        side_effect=httpx.ConnectTimeout("sin respuesta")
    )
    with pytest.raises(LoginSocialNoValidoException):
        ProveedoresConfigurados().de(Proveedor.GOOGLE).url_de_autorizacion(transaccion())


# ── Apple ──


def test_apple_se_autentica_con_un_jwt_es256_de_vida_corta(proveedores):
    completar(Proveedor.APPLE, proveedores.apple, email="x7k2@privaterelay.appleid.com", email_verified="true")
    canje = proveedores.apple.canjes[0]
    assert canje["client_id"] == "com.example.gastos.web" and canje["_autorizacion"] is None  # client_secret_post
    assert "code_verifier" not in canje  # no hubo challenge
    publica = ECKey.import_key(proveedores.clave_apple.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))  # fmt: skip
    secreto = jwt.decode(canje["client_secret"], publica, algorithms=["ES256"])
    assert secreto.header == {"alg": "ES256", "kid": "CLAVE12345", "typ": "JWT"}
    c = secreto.claims
    assert (c["iss"], c["sub"], c["aud"]) == ("EQUIPO1234", "com.example.gastos.web", "https://appleid.apple.example")
    assert 0 < c["exp"] - c["iat"] <= 300


def test_apple_el_nombre_de_user_y_el_email_del_id_token(proveedores):
    adapter = ProveedoresConfigurados().de(Proveedor.APPLE)
    t = transaccion(Proveedor.APPLE)
    vuelta = proveedores.apple.autorizar(adapter.url_de_autorizacion(t), email="x7k2@privaterelay.appleid.com",
                                         email_verified="true", given_name=None, family_name=None)  # fmt: skip
    # `user` llega en el POST (solo la primera vez) y no va firmado: de ahí solo se toma el nombre
    user = json.dumps({"name": {"firstName": "Ana", "lastName": "García"}, "email": "otra@example.com"})
    perfil = adapter.completar(t, vuelta | {"user": user})
    assert perfil == PerfilExterno(Proveedor.APPLE, "1081", "x7k2@privaterelay.appleid.com", True, "Ana", "García")


# ── GitHub: sin ID token ──


def test_github_pregunta_a_su_api_y_usa_el_id_no_el_login(proveedores):
    perfil = completar(Proveedor.GITHUB, proveedores.github)
    assert perfil == PerfilExterno(Proveedor.GITHUB, "583231", "ana@gmail.com", True, "Ana García")
    canje = proveedores.github.canjes[0]
    assert canje["client_secret"] == "secreto-github" and canje["code_verifier"] == "v" * 64


def test_github_un_email_principal_sin_verificar_no_cuenta(proveedores):
    proveedores.github.correos = [{"email": "ana@gmail.com", "primary": True, "verified": False}]
    assert completar(Proveedor.GITHUB, proveedores.github).email_verificado is False


def test_github_avisa_de_los_errores_con_un_200(proveedores):
    adapter = ProveedoresConfigurados().de(Proveedor.GITHUB)
    adapter.url_de_autorizacion(transaccion(Proveedor.GITHUB))
    with pytest.raises(LoginSocialNoValidoException):  # {"error": "bad_verification_code"} con status 200
        adapter.completar(transaccion(Proveedor.GITHUB), {"code": "inventado"})
    proveedores.github.usuario = {"login": "sin-id"}
    with pytest.raises(LoginSocialNoValidoException):
        completar(Proveedor.GITHUB, proveedores.github)


def test_los_tokens_del_proveedor_no_salen_del_adapter(proveedores):
    perfil = completar(Proveedor.GOOGLE, proveedores.google)
    assert TOKEN_DEL_PROVEEDOR not in repr(perfil)  # el perfil solo lleva quién es
