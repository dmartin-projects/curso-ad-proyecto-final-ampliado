"""Ejercicio 1 del módulo 91: Microsoft Entra ID como cuarto proveedor (solo un adapter y su configuración)."""

import pytest
from django.test import Client

from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.vo.transaccion_social import TransaccionSocial
from usuarios.infrastructure.providers.proveedores_configurados import ProveedoresConfigurados
from usuarios.models import Usuario
from usuarios.tests.infrastructure.api.v1.test_social_api import S, con_sesion, destino, entrar, error, vuelta
from usuarios.tests.infrastructure.proveedor_falso import OIDCFalso

pytestmark = pytest.mark.django_db
MS = "https://login.microsoftonline.example/common/v2.0"
TENANT = "9188040d-6c67-4c5b-b112-36a304b66dad"


@pytest.fixture
def microsoft(proveedores, settings):
    settings.SOCIAL_LOGIN = settings.SOCIAL_LOGIN | {
        "microsoft": {"client_id": "gastos-entra", "client_secret": "secreto-entra", "emisor": MS}
    }
    falso = OIDCFalso(proveedores.http, MS, "gastos-entra")
    falso.metadatos["issuer"] = "https://login.microsoftonline.example/{tenantid}/v2.0"  # como el de verdad
    falso.trampas = {"iss": f"https://login.microsoftonline.example/{TENANT}/v2.0"}
    falso.claims = falso.claims | {"tid": TENANT, "email_verified": None}  # Entra no manda email_verified
    return falso


def completar(falso, **claims):
    adapter = ProveedoresConfigurados().de(Proveedor.MICROSOFT)
    t = TransaccionSocial(Proveedor.MICROSOFT, "s", "n", "v" * 64, Proposito.ENTRAR)
    return adapter.completar(t, falso.autorizar(adapter.url_de_autorizacion(t), **claims))


def test_el_iss_es_el_de_su_tenant(microsoft):
    assert completar(microsoft).sub == "1081"
    for iss, tid in [
        (f"https://login.microsoftonline.example/{TENANT}/v2.0", "otro-tenant"),  # el iss no es el de su tid
        ("https://login.microsoftonline.example/{tenantid}/v2.0", TENANT),  # la plantilla, literal
        (MS, TENANT),
        (f"https://login.microsoftonline.example/{TENANT}/v2.0", None),  # sin tid
    ]:
        microsoft.trampas = {"iss": iss}
        with pytest.raises(LoginSocialNoValidoException):
            completar(microsoft, tid=tid)


def test_el_iss_de_la_vuelta_es_el_de_su_tenant(microsoft):
    """RFC 9207: el `iss` de la vuelta lleva el tenant, que solo dice el ID token. Antes del canje, que sea de
    Microsoft con un tenant; después, el mismo que el del ID token."""

    def con_iss(iss):
        adapter = ProveedoresConfigurados().de(Proveedor.MICROSOFT)
        t = TransaccionSocial(Proveedor.MICROSOFT, "s", "n", "v" * 64, Proposito.ENTRAR)
        return adapter.completar(t, microsoft.autorizar(adapter.url_de_autorizacion(t)) | {"iss": iss})

    assert con_iss(f"https://login.microsoftonline.example/{TENANT}/v2.0").sub == "1081"
    canjes = len(microsoft.canjes)
    for iss in ("https://login.microsoftonline.example/{tenantid}/v2.0", MS, f"https://otro.example/{TENANT}/v2.0"):
        with pytest.raises(LoginSocialNoValidoException):
            con_iss(iss)
    assert len(microsoft.canjes) == canjes  # ni se ha canjeado el code: el mix-up se para antes
    with pytest.raises(LoginSocialNoValidoException):  # de Microsoft, pero de otro tenant que el del ID token
        con_iss("https://login.microsoftonline.example/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0")


def test_el_email_solo_cuenta_como_verificado_con_xms_edov(microsoft):
    assert completar(microsoft).email_verificado is False  # nOAuth: lo pone el administrador del tenant
    assert completar(microsoft, email_verified=True).email_verificado is False  # ni aunque lo diga
    assert completar(microsoft, xms_edov=True).email_verificado is True


def test_sin_email_verificado_se_vincula_desde_dentro(microsoft):
    navegador = Client()
    datos = microsoft.autorizar(entrar(navegador, "microsoft"))
    assert error(vuelta(navegador, "microsoft", datos)) == "email_no_verificado"
    ana = con_sesion(Usuario.objects.create_user("ana@empresa.example", "una-clave-muy-larga"))
    r = ana.post(S + "microsoft/vincular/")
    navegador = Client()
    navegador.cookies["social_microsoft"] = r.cookies["social_microsoft"].value
    assert destino(vuelta(navegador, "microsoft", microsoft.autorizar(r.json()["url"])))[1] == {
        "vinculada": "microsoft"
    }
    navegador = Client()  # y desde ahora entra con Microsoft
    assert destino(vuelta(navegador, "microsoft", microsoft.autorizar(entrar(navegador, "microsoft"))))[0].endswith("/")
    assert {"id": "microsoft", "nombre": "Microsoft"} in Client().get(S).json()["proveedores"]
