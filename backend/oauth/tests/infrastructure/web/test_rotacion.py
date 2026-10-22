"""Rotar la clave que firma los ID tokens sin invalidar los que están en vuelo (ejercicio 2 del módulo 90)."""

import jwt
import pytest
from django.test import Client

from conftest import UsuarioFactory
from oauth.infrastructure.crypto.claves import nueva_clave_pem
from oauth.tests.infrastructure.flujo import registrar, tokens

pytestmark = pytest.mark.django_db


@pytest.fixture
def claves(settings):
    """fase(activa, inactivas): cambia las claves como lo haría un despliegue (OIDC_RSA_PRIVATE_KEY*)."""

    def fase(activa, *inactivas):
        settings.OAUTH2_PROVIDER = {
            **settings.OAUTH2_PROVIDER,
            "OIDC_RSA_PRIVATE_KEY": activa,
            "OIDC_RSA_PRIVATE_KEYS_INACTIVE": list(inactivas),
        }

    return fase


def jwks():
    return Client().get("/api/oauth/.well-known/jwks.json").json()


def verificar(id_token, conjunto):
    """Como cualquier cliente: la clave del JWKS con el kid del token, o ninguna."""
    kid = jwt.get_unverified_header(id_token)["kid"]
    clave = next((k for k in conjunto["keys"] if k["kid"] == kid), None)
    if clave is None:
        raise LookupError(f"kid desconocido: {kid}")
    return jwt.decode(id_token, jwt.PyJWK(clave).key, algorithms=["RS256"], audience="gastos-cli",
                      options={"verify_iss": False})  # fmt: skip


def test_rotar_en_tres_pasos(claves):
    registrar()
    ana = UsuarioFactory()
    vieja, nueva = nueva_clave_pem(), nueva_clave_pem()

    claves(vieja)
    en_vuelo = tokens(ana)["id_token"]  # emitido antes de rotar: tiene que seguir valiendo
    (kid_viejo,) = [k["kid"] for k in jwks()["keys"]]

    # 1. Publicar la nueva sin firmar con ella: los clientes la conocerán antes de ver un token firmado con ella
    claves(vieja, nueva)
    assert len(jwks()["keys"]) == 2
    assert jwt.get_unverified_header(tokens(ana)["id_token"])["kid"] == kid_viejo

    # 2. Firmar con la nueva; la vieja sigue en el JWKS
    claves(nueva, vieja)
    recien = tokens(ana)["id_token"]
    kid_nuevo = jwt.get_unverified_header(recien)["kid"]
    assert kid_nuevo != kid_viejo and {k["kid"] for k in jwks()["keys"]} == {kid_viejo, kid_nuevo}
    assert verificar(en_vuelo, jwks())["sub"] == verificar(recien, jwks())["sub"] == str(ana.pk)

    # 3. Retirar la vieja (pasados los 10 minutos que dura un ID token): lo firmado con ella ya no se verifica
    claves(nueva)
    assert [k["kid"] for k in jwks()["keys"]] == [kid_nuevo]
    verificar(recien, jwks())
    with pytest.raises(LookupError):
        verificar(en_vuelo, jwks())


def test_los_access_tokens_no_dependen_de_la_clave(claves):
    """Son opacos: rotar la clave de los ID tokens no cierra ninguna sesión."""
    registrar()
    claves(nueva_clave_pem())
    t = tokens(UsuarioFactory())
    claves(nueva_clave_pem())
    assert Client().get("/api/oauth/userinfo/", HTTP_AUTHORIZATION=f"Bearer {t['access_token']}").status_code == 200
