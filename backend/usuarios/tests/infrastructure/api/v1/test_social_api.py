"""El social login de punta a punta en el backend (módulo 91): el navegador es el Client de Django, los proveedores
son de mentira (respx) y todo lo demás es de verdad (vistas, use cases, caché, base de datos, simplejwt)."""

import json
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from django.test import Client
from rest_framework.test import APIClient

from conftest import UsuarioFactory
from usuarios.models import IdentidadExterna, Usuario
from usuarios.tests.infrastructure.proveedor_falso import TOKEN_DEL_PROVEEDOR

pytestmark = pytest.mark.django_db
A, S = "/api/v1/auth/", "/api/v1/auth/social/"
SPA = "https://gastos.example"


def entrar(navegador: Client, proveedor="google", volver=None) -> str:
    r = navegador.get(f"{S}{proveedor}/entrar/", {"volver": volver} if volver else {})
    assert r.status_code == 302, r.content
    return r["Location"]


def vuelta(navegador: Client, proveedor: str, datos: dict):
    """El navegador vuelve del proveedor: GET con la query; Apple, POST de formulario (form_post)."""
    url = f"{S}{proveedor}/vuelta/"
    if proveedor == "apple":
        return navegador.post(url, urlencode(datos), content_type="application/x-www-form-urlencoded")
    return navegador.get(url, datos)


def destino(r) -> tuple[str, dict]:
    assert r.status_code == 302, r.content
    partes = urlsplit(r["Location"])
    return f"{partes.scheme}://{partes.netloc}{partes.path}", {k: v[0] for k, v in parse_qs(partes.query).items()}


def error(r) -> str | None:
    return destino(r)[1].get("error_social")


def login_google(navegador: Client, falso, volver=None, **claims):
    return vuelta(navegador, "google", falso.autorizar(entrar(navegador, volver=volver), **claims))


# ── Entrar ──


def test_entrar_con_google_por_primera_vez_crea_la_cuenta_y_abre_la_sesion_de_siempre(proveedores):
    navegador = Client()
    ida = entrar(navegador, volver="/hogares/3")
    cookie = navegador.cookies["social_google"]
    assert ida.startswith("https://accounts.google.example/authorize?")
    assert (cookie["path"], cookie["httponly"], cookie["samesite"]) == ("/api/v1/auth/social/google/", True, "Lax")

    r = vuelta(navegador, "google", proveedores.google.autorizar(ida))
    assert destino(r) == (f"{SPA}/hogares/3", {})  # de vuelta a la SPA, adonde iba
    assert r.cookies["refresh"]["httponly"] and r.cookies["refresh"]["path"] == "/api/v1/auth/"
    assert r.cookies["social_google"].value == "" and "no-store" in r["Cache-Control"]  # la cookie, gastada
    # Patrón BFF: lo del proveedor no llega al navegador (ni en la URL, ni en una cookie, ni en el cuerpo)
    assert TOKEN_DEL_PROVEEDOR not in r["Location"] + str(r.cookies) + r.content.decode()

    ana = Usuario.objects.get(email="ana@gmail.com")
    assert (ana.is_active, ana.has_usable_password(), ana.nombre, ana.apellidos) == (True, False, "Ana", "García")
    assert list(ana.identidades.values_list("proveedor", "sub")) == [("google", "1081")]
    # La SPA, al arrancar, pide su access token con el refresh de siempre
    access = navegador.post(A + "refresh/").json()["access"]
    assert APIClient(HTTP_AUTHORIZATION=f"Bearer {access}").get(A + "me/").json()["email"] == "ana@gmail.com"


def test_la_segunda_vez_entra_en_la_misma_cuenta_aunque_el_email_haya_cambiado(proveedores):
    login_google(Client(), proveedores.google)
    r = login_google(Client(), proveedores.google, email="ana.garcia@gmail.com")
    assert destino(r) == (f"{SPA}/", {}) and Usuario.objects.count() == 1  # la identidad es el sub
    assert IdentidadExterna.objects.get().ultimo_uso is not None


# ── Las defensas de la vuelta ──


@pytest.mark.parametrize("caso", ["sin state", "otro state", "sin la cookie", "de otro navegador"])
def test_una_vuelta_que_no_empezo_aqui_no_canjea_nada(proveedores, caso):
    navegador = Client()
    datos = proveedores.google.autorizar(entrar(navegador))
    match caso:
        case "sin state":
            del datos["state"]
        case "otro state":
            datos["state"] = "el-del-atacante"
        case "sin la cookie":
            del navegador.cookies["social_google"]
        case "de otro navegador":  # CSRF en la vuelta: la víctima llega con el code y el state del atacante
            navegador = Client()
            entrar(navegador)
    assert error(vuelta(navegador, "google", datos)) == "estado_no_valido"
    assert proveedores.google.token.call_count == 0 and not Usuario.objects.exists()


def test_la_vuelta_caduca(proveedores, time_machine):
    time_machine.move_to(datetime.now(UTC), tick=True)
    navegador = Client()
    datos = proveedores.google.autorizar(entrar(navegador))
    time_machine.shift(601)  # SOCIAL_LOGIN_SEGUNDOS: la transacción ya no está en la caché
    assert error(vuelta(navegador, "google", datos)) == "estado_no_valido"


def test_la_vuelta_no_se_puede_reutilizar(proveedores):
    navegador = Client()
    datos = proveedores.google.autorizar(entrar(navegador))
    cookie = navegador.cookies["social_google"].value
    assert destino(vuelta(navegador, "google", datos))[0] == f"{SPA}/"
    navegador.cookies["social_google"] = cookie  # la misma petición otra vez (un historial, un log, un atacante)
    assert error(vuelta(navegador, "google", datos)) == "estado_no_valido"
    assert proveedores.google.token.call_count == 1


@pytest.mark.parametrize("proveedor", ["google", "apple"])
def test_un_code_de_otra_sesion_no_sirve(proveedores, proveedor):
    """Code injection: el atacante consigue un code de SU cuenta y lo mete en la vuelta del navegador de la víctima
    (con el state de la víctima). Google tiene PKCE y nonce; Apple, que no anuncia PKCE, solo el nonce."""
    falso = getattr(proveedores, proveedor)
    del_atacante = falso.autorizar(entrar(Client(), proveedor), sub="atacante", email="malo@example.com")
    victima = Client()
    de_la_victima = falso.autorizar(entrar(victima, proveedor))
    r = vuelta(victima, proveedor, {"code": del_atacante["code"], "state": de_la_victima["state"]})
    assert error(r) == "login_social_no_valido" and not Usuario.objects.exists()


def test_un_id_token_que_no_es_para_gastos_no_abre_nada(proveedores):
    proveedores.google.trampas = {"aud": "otra-aplicacion"}
    assert error(login_google(Client(), proveedores.google)) == "login_social_no_valido"
    assert not Usuario.objects.exists()


@pytest.mark.parametrize("volver", ["//otra.example/robar", "https://otra.example", "/\\otra.example", "javascript:x"])
def test_volver_solo_lleva_a_la_spa(proveedores, volver):
    r = login_google(Client(), proveedores.google, volver=volver)
    assert destino(r) == (f"{SPA}/", {})


def test_si_cancela_vuelve_al_login_con_el_motivo(proveedores):
    navegador = Client()
    datos = proveedores.google.autorizar(entrar(navegador))
    r = vuelta(navegador, "google", {"error": "access_denied", "state": datos["state"]})
    assert destino(r) == (f"{SPA}/login", {"error_social": "acceso_cancelado", "proveedor": "google"})


def test_un_proveedor_que_no_esta_configurado(proveedores, settings):
    del settings.SOCIAL_LOGIN["github"]
    assert error(Client().get(S + "github/entrar/")) == "proveedor_no_disponible"
    assert error(Client().get(S + "facebook/entrar/")) == "proveedor_no_disponible"
    assert [p["id"] for p in Client().get(S).json()["proveedores"]] == ["google", "apple"]


# ── Quién puede entrar ──


@pytest.mark.parametrize("proveedor", ["google", "github"])
def test_sin_email_verificado_no_se_crea_ninguna_cuenta(proveedores, proveedor):
    navegador = Client()
    if proveedor == "google":
        datos = proveedores.google.autorizar(entrar(navegador), email_verified=False)
    else:
        proveedores.github.correos = [{"email": "ana@gmail.com", "primary": True, "verified": False}]
        datos = proveedores.github.autorizar(entrar(navegador, "github"))
    assert error(vuelta(navegador, proveedor, datos)) == "email_no_verificado"
    assert not Usuario.objects.exists()


@pytest.mark.parametrize("activa", [True, False], ids=["con la cuenta activa", "con el registro sin completar"])
def test_el_email_de_una_cuenta_existente_no_da_acceso_a_ella(proveedores, activa):
    """Account takeover: alguien con un Google (o lo que sea) que dice ser ana@gmail.com no entra en la cuenta de
    Ana. Ni tampoco "reclama" un registro sin completar con ese email: eso solo lo hace quien abre el enlace del
    correo (módulo 35)."""
    if activa:
        ana = UsuarioFactory(email="ana@gmail.com")
    else:
        ana = Usuario.objects.create_user("ana@gmail.com", None, is_active=False)  # registrada, sin contraseña
    navegador = Client()
    r = login_google(navegador, proveedores.google)
    assert destino(r) == (f"{SPA}/login", {"error_social": "cuenta_existente", "proveedor": "google"})
    assert "refresh" not in r.cookies and not IdentidadExterna.objects.exists()
    assert Usuario.objects.get() == ana and Usuario.objects.get().password == ana.password  # sin tocar


def test_una_cuenta_desactivada_no_entra_ni_con_su_proveedor(proveedores):
    login_google(Client(), proveedores.google)
    Usuario.objects.update(is_active=False)  # desactivada por soporte
    r = login_google(Client(), proveedores.google)
    assert error(r) == "cuenta_desactivada" and "refresh" not in r.cookies


# ── Apple: form_post ──


def test_apple_vuelve_con_un_post_y_su_cookie_es_samesite_none(proveedores):
    navegador = Client()
    ida = entrar(navegador, "apple")
    cookie = navegador.cookies["social_apple"]
    assert (cookie["samesite"], cookie["secure"]) == ("None", True)  # Lax no viajaría en un POST desde Apple
    datos = proveedores.apple.autorizar(ida, email="x7k2@privaterelay.appleid.com", email_verified="true")
    user = json.dumps({"name": {"firstName": "Ana", "lastName": "García"}})
    r = vuelta(navegador, "apple", datos | {"user": user})
    assert destino(r) == (f"{SPA}/", {}) and r.cookies["refresh"]
    ana = Usuario.objects.get(email="x7k2@privaterelay.appleid.com")
    assert (ana.nombre, ana.apellidos) == ("Ana", "García")


def test_apple_cancelado(proveedores):
    navegador = Client()
    datos = proveedores.apple.autorizar(entrar(navegador, "apple"))
    r = vuelta(navegador, "apple", {"error": "user_cancelled_authorize", "state": datos["state"]})
    assert error(r) == "acceso_cancelado"


# ── Vincular y desvincular, desde dentro ──


def con_sesion(usuario) -> APIClient:
    c = APIClient()
    c.force_authenticate(usuario)
    return c


def test_vincular_google_a_mi_cuenta_y_entrar_con_el(proveedores):
    luis = UsuarioFactory(email="luis@trabajo.example")
    api = con_sesion(luis)
    r = api.post(S + "google/vincular/")
    assert r.status_code == 200 and r.cookies["social_google"]["httponly"]
    navegador = Client()
    navegador.cookies["social_google"] = r.cookies["social_google"].value  # el mismo navegador que la SPA
    datos = proveedores.google.autorizar(r.json()["url"], sub="luis-google", email="luis.personal@gmail.com")
    assert destino(vuelta(navegador, "google", datos)) == (f"{SPA}/acceso", {"vinculada": "google"})
    assert luis.identidades.get().sub == "luis-google"
    # Desde ahora, Google lleva a su cuenta (con otro email)
    assert destino(login_google(Client(), proveedores.google, sub="luis-google"))[0] == f"{SPA}/"
    assert APIClient().post(S + "google/vincular/").status_code == 401  # solo con sesión


def test_no_se_puede_vincular_el_google_de_otro(proveedores):
    login_google(Client(), proveedores.google)  # ana@gmail.com: sub 1081
    luis = con_sesion(UsuarioFactory())
    r = luis.post(S + "google/vincular/")
    navegador = Client()
    navegador.cookies["social_google"] = r.cookies["social_google"].value
    datos = proveedores.google.autorizar(r.json()["url"])  # sub 1081: el de Ana
    assert destino(vuelta(navegador, "google", datos)) == (
        f"{SPA}/acceso", {"error_social": "identidad_de_otra_cuenta", "proveedor": "google"}
    )  # fmt: skip


def test_metodos_de_acceso_sin_quedarse_nunca_sin_ninguno(proveedores):
    login_google(Client(), proveedores.google)
    api = con_sesion(Usuario.objects.get())
    acceso = api.get(A + "acceso/").json()
    assert acceso["contrasena"] is False
    assert [(i["proveedor"], i["nombre"], i["email"]) for i in acceso["identidades"]] == [
        ("google", "Google", "ana@gmail.com")
    ]
    r = api.delete(A + "acceso/google/")
    assert (r.status_code, r.json()["type"]) == (409, "ultimo_metodo_de_acceso")
    r = api.post(A + "establecer-password/", {"nueva": "123"})
    assert r.status_code == 400 and set(r.json()["errors"]) == {"nueva"}
    assert api.post(A + "establecer-password/", {"nueva": "una-clave-muy-larga-77"}).status_code == 204
    assert api.post(A + "establecer-password/", {"nueva": "otra-clave-muy-larga"}).status_code == 409
    assert api.delete(A + "acceso/google/").status_code == 204
    assert api.get(A + "acceso/").json() == {"contrasena": True, "identidades": []}
    assert api.delete(A + "acceso/google/").status_code == 404
    r = APIClient().post(A + "login/", {"email": "ana@gmail.com", "password": "una-clave-muy-larga-77"})
    assert r.status_code == 200


def test_una_cuenta_sin_contrasena_no_entra_con_contrasena(proveedores):
    login_google(Client(), proveedores.google)
    for password in ("", "!"):  # set_unusable_password guarda "!…": ni eso ni nada vale
        assert APIClient().post(A + "login/", {"email": "ana@gmail.com", "password": password}).status_code in (
            400,
            401,
        )


def test_lista_de_proveedores_con_el_origen_de_la_app(proveedores):
    assert Client().get(S).json() == {
        "origen": SPA,
        "proveedores": [{"id": "google", "nombre": "Google"}, {"id": "github", "nombre": "GitHub"},
                        {"id": "apple", "nombre": "Apple"}],
    }  # fmt: skip


# ── Ejercicio 2: el aviso al vincular ──


def test_al_vincular_llega_un_aviso_al_email_de_gastos(proveedores, django_capture_on_commit_callbacks, mailoutbox):
    luis = UsuarioFactory(email="luis@trabajo.example")
    r = con_sesion(luis).post(S + "github/vincular/")
    navegador = Client()
    navegador.cookies["social_github"] = r.cookies["social_github"].value
    with django_capture_on_commit_callbacks(execute=True):
        vuelta(navegador, "github", proveedores.github.autorizar(r.json()["url"]))
    (aviso,) = mailoutbox
    assert aviso.to == ["luis@trabajo.example"]  # el de Gastos, no el de GitHub
    assert aviso.subject == "Has vinculado GitHub a tu cuenta de Gastos"
    assert "(ana@gmail.com)" in aviso.body and "https://gastos.example/acceso" in aviso.body


# ── Ejercicio 3: entrar con un proveedor en el authorization server (módulo 90) ──


def test_una_cuenta_sin_contrasena_autoriza_una_aplicacion_entrando_con_google(proveedores):
    from oauth.tests.infrastructure.flujo import peticion, pkce, registrar

    login_google(Client(), proveedores.google)  # ana: creada con Google, sin contraseña
    registrar()  # gastos-cli
    navegador = Client()
    autorizar = navegador.get("/api/oauth/authorize/", peticion(pkce()[1]))
    login = navegador.get(autorizar["Location"])  # el login del authorization server, con su `next`
    siguiente = parse_qs(urlsplit(autorizar["Location"]).query)["next"][0]  # /api/oauth/authorize/?response_type=…
    ida = dict(login.context["proveedores"])["Google"]
    assert parse_qs(urlsplit(ida).query) == {"para": ["autorizar"], "volver": [siguiente]}
    r = navegador.get(ida)
    r = vuelta(navegador, "google", proveedores.google.autorizar(r["Location"]))
    url, _ = destino(r)
    assert url == f"{SPA}/api/oauth/authorize/"  # de vuelta a la misma petición de autorización
    assert r.cookies["sessionid"]["path"] == "/api/oauth/" and "refresh" not in r.cookies  # la sesión del AS, no la SPA
    consentimiento = navegador.get(r["Location"].removeprefix(SPA))
    assert consentimiento.status_code == 200
    assert "ana@gmail.com" in consentimiento.content.decode()  # «Has entrado como ana@gmail.com»


def test_desde_el_authorization_server_solo_se_vuelve_a_authorize(proveedores):
    navegador = Client()
    ida = navegador.get(S + "google/entrar/", {"para": "autorizar", "volver": "https://otra.example/"})["Location"]
    r = vuelta(navegador, "google", proveedores.google.autorizar(ida))
    assert destino(r) == (f"{SPA}/api/oauth/login/", {})


def test_un_error_vuelve_al_login_del_authorization_server_con_su_peticion(proveedores):
    UsuarioFactory(email="ana@gmail.com")
    navegador = Client()
    siguiente = "/api/oauth/authorize/?client_id=gastos-cli"
    ida = navegador.get(S + "google/entrar/", {"para": "autorizar", "volver": siguiente})["Location"]
    r = vuelta(navegador, "google", proveedores.google.autorizar(ida))
    assert destino(r) == (
        f"{SPA}/api/oauth/login/", {"next": siguiente, "error_social": "cuenta_existente", "proveedor": "google"}
    )  # fmt: skip
    pagina = navegador.get(r["Location"].removeprefix(SPA))
    assert "Ya hay una cuenta con ese email: entra con tu contraseña." in pagina.content.decode()


def test_el_login_con_contrasena_del_authorization_server_pasa_por_iniciar_sesion(monkeypatch):
    from usuarios.domain.enums.canal import Canal
    from usuarios.infrastructure import container

    llamadas = []
    original = container.iniciar_sesion

    class Espia:
        def ejecutar(self, entrada):
            llamadas.append((entrada.usuario_id, entrada.canal))
            return original().ejecutar(entrada)

    monkeypatch.setattr(container, "iniciar_sesion", Espia)
    ana = UsuarioFactory(email="ana@example.com")
    r = Client().post("/api/oauth/login/", {"username": "ana@example.com", "password": "clave-segura-123"})
    assert r.status_code == 302 and llamadas == [(ana.pk, Canal.AUTORIZACION)]
