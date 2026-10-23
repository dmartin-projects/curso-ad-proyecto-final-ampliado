"""El segundo factor, las passkeys, el step-up y las sesiones de punta a punta en el backend (módulo 92): el navegador
es el APIClient (guarda las cookies), y todo lo demás es de verdad: vistas, use cases, caché, PostgreSQL y simplejwt."""

from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from django.core import mail
from django.db import connection
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from conftest import UsuarioFactory
from usuarios.application.empezar_registro_passkey_use_case.dtos.empezar_registro_passkey_input_dto import (
    EmpezarRegistroPasskeyInputDTO,
)
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.registrar_passkey_use_case.dtos.registrar_passkey_input_dto import RegistrarPasskeyInputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container
from usuarios.infrastructure.auth.enlaces_django import EnlacesDjango
from usuarios.models import SegundoFactor, Sesion
from usuarios.tests.infrastructure.autenticador_falso import AutenticadorFalso
from usuarios.tests.infrastructure.ayudas_mfa import (
    CHROME_MAC,
    SAFARI_IPHONE,
    A,
    activar_mfa,
    codigo,
    con_access,
    login,
    navegador,
)

pytestmark = pytest.mark.django_db


def entrar(usuario, user_agent=CHROME_MAC):
    c = navegador(user_agent)
    return con_access(c, login(c, usuario))


# ── El login en dos pasos ──


def test_activar_el_mfa_y_entrar_en_dos_pasos(django_capture_on_commit_callbacks):
    ana = UsuarioFactory(email="ana@example.com")
    spa = entrar(ana)
    alta = spa.post(A + "seguridad/totp/").json()
    assert alta["uri"].startswith("otpauth://totp/Gastos:ana%40example.com?secret=") and alta["qr"].startswith("data:")
    r = spa.post(A + "seguridad/totp/confirmar/", {"codigo": "000000"})
    assert (r.status_code, r.json()["errors"]) == (400, {"codigo": ["El código no es correcto o ya se ha usado."]})
    with django_capture_on_commit_callbacks(execute=True):
        codigos = spa.post(A + "seguridad/totp/confirmar/", {"codigo": codigo(alta["secreto"], -30)}).json()["codigos"]
    assert len(codigos) == 10 and spa.get(A + "seguridad/").json()["mfa"] is True
    assert mail.outbox[-1].subject == "Cambio de seguridad en tu cuenta de Gastos"

    # Otro día, otro navegador: la contraseña ya no basta
    c = navegador()
    r = login(c, ana)
    assert r.status_code == 200 and r.json() == {"segundo_factor": ["totp", "recuperacion"]}
    assert "refresh" not in r.cookies  # ni sesión ni access: solo el login a medias
    pendiente = r.cookies["mfa"]
    assert (pendiente["httponly"], pendiente["path"], pendiente["samesite"]) == (True, "/api/v1/auth/", "Strict")
    assert c.get(A + "mfa/").json() == {"factores": ["totp", "recuperacion"]}
    r = c.post(A + "mfa/", {"factor": "totp", "codigo": codigo(alta["secreto"])})
    assert r.status_code == 200 and r.cookies["refresh"]["httponly"] and r.cookies["mfa"].value == ""
    assert con_access(navegador(), r).get(A + "me/").json()["email"] == "ana@example.com"
    assert Sesion.objects.filter(usuario=ana).latest("creada").factores == ["contrasena", "totp"]


def test_un_codigo_de_recuperacion_vale_una_vez():
    ana = UsuarioFactory()
    _, codigos = activar_mfa(ana)
    c = navegador()
    login(c, ana)
    assert c.post(A + "mfa/", {"factor": "recuperacion", "codigo": codigos[0].lower()}).status_code == 200
    c = navegador()
    login(c, ana)
    r = c.post(A + "mfa/", {"factor": "recuperacion", "codigo": codigos[0]})
    assert r.status_code == 400 and "codigo" in r.json()["errors"]


def test_sin_la_cookie_del_primer_paso_no_hay_segundo():
    ana = UsuarioFactory()
    secreto, _ = activar_mfa(ana)
    r = navegador().post(A + "mfa/", {"factor": "totp", "codigo": codigo(secreto)})
    assert (r.status_code, r.json()["type"]) == (401, "login_pendiente_no_valido")


def test_cinco_fallos_bloquean_el_segundo_factor_de_la_cuenta():
    ana = UsuarioFactory()
    secreto, _ = activar_mfa(ana)
    c = navegador()
    login(c, ana)
    for _ in range(4):
        assert c.post(A + "mfa/", {"factor": "totp", "codigo": "000000"}).status_code == 400
    c = navegador()
    login(c, ana)  # volver a empezar con la contraseña no reinicia la cuenta de fallos…
    assert c.post(A + "mfa/", {"factor": "totp", "codigo": "000000"}).status_code == 400  # el quinto
    r = c.post(A + "mfa/", {"factor": "totp", "codigo": codigo(secreto)})  # …y ni el código bueno, durante un minuto
    assert (r.status_code, r.json()["type"]) == (429, "segundo_factor_bloqueado")
    assert 0 < int(r["Retry-After"]) <= 61


def test_tras_el_techo_de_fallos_solo_se_desbloquea_recuperando_la_cuenta(
    monkeypatch, django_capture_on_commit_callbacks
):
    """NIST SP 800-63B-4: como mucho 100 fallos seguidos. Ni el límite por login pendiente (se vuelve a poner la
    contraseña) ni el de cada IP (se reparten entre muchas) ponen un techo: el de la cuenta, sí."""
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", {**ScopedRateThrottle.THROTTLE_RATES, "mfa": "10000/min"})
    ana = UsuarioFactory(email="ana@example.com")
    secreto, _ = activar_mfa(ana)
    SegundoFactor.objects.filter(usuario=ana).update(fallos=99)  # p. ej., tras días de intentos y esperas
    c = navegador()
    login(c, ana)
    with django_capture_on_commit_callbacks(execute=True):
        assert c.post(A + "mfa/", {"factor": "totp", "codigo": "000000"}).status_code == 400  # el fallo 100
    assert "bloqueada" in mail.outbox[-1].body  # el aviso: quien prueba códigos tiene la contraseña
    for _ in range(3):
        c = navegador()
        login(c, ana)
        r = c.post(A + "mfa/", {"factor": "totp", "codigo": codigo(secreto)})  # ni con el bueno, ni esperando
        assert (r.status_code, r.json()["type"]) == (429, "segundo_factor_bloqueado_hasta_recuperar")
        assert "Retry-After" not in r
    assert SegundoFactor.objects.get(usuario=ana).fallos == 100
    # La salida: el enlace de recuperación (llega a su email) y una contraseña nueva
    q = parse_qs(urlsplit(EnlacesDjango().crear(ana.pk, "nueva-password")).query)
    datos = {"uid": q["uid"][0], "token": q["token"][0], "password": "otra-clave-larga-987"}
    assert navegador().post(A + "recuperar-password/confirmar/", datos).status_code == 204
    c = navegador()
    login(c, ana, "otra-clave-larga-987")
    assert c.post(A + "mfa/", {"factor": "totp", "codigo": codigo(secreto)}).status_code == 200


def test_una_sesion_sin_mfa_no_lo_activa_con_un_codigo_de_otra_app():
    ana = UsuarioFactory()
    spa = entrar(ana)
    spa.post(A + "seguridad/totp/")
    r = spa.post(A + "seguridad/totp/confirmar/", {"codigo": codigo("JBSWY3DPEHPK3PXP")})
    assert r.status_code == 400 and spa.get(A + "seguridad/").json()["mfa"] is False


# ── Step-up ──


def test_una_accion_sensible_pide_reautenticar_y_luego_se_repite(time_machine):
    ana = UsuarioFactory()
    spa = entrar(ana)
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=6))  # el access sigue valiendo (10 min)…
    r = spa.post(A + "seguridad/totp/")
    assert (r.status_code, r.json()["type"]) == (401, "reautenticacion_requerida")  # …pero no es "reciente"
    assert r["WWW-Authenticate"] == (
        'Bearer realm="api", error="insufficient_user_authentication", '
        'error_description="A more recent authentication is required", max_age="300"'
    )  # RFC 9470
    assert spa.get(A + "reautenticar/").json() == {"factores": ["contrasena"], "proveedores": [], "max_age": 300}
    r = spa.post(A + "reautenticar/", {"factor": "contrasena", "codigo": "mala"})
    assert r.status_code == 400 and "password" in r.json()["errors"]
    assert spa.post(A + "reautenticar/", {"factor": "contrasena", "codigo": "clave-segura-123"}).status_code == 204
    assert spa.post(A + "seguridad/totp/").status_code == 200  # la misma petición, ahora sí


def test_con_mfa_el_step_up_es_con_el_segundo_factor(time_machine):
    ana = UsuarioFactory()
    secreto, _ = activar_mfa(ana)
    c = navegador()
    login(c, ana)
    spa = con_access(navegador(), c.post(A + "mfa/", {"factor": "totp", "codigo": codigo(secreto)}))
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=6))
    assert spa.get(A + "reautenticar/").json()["factores"] == ["totp"]
    r = spa.post(A + "reautenticar/", {"factor": "contrasena", "codigo": "clave-segura-123"})
    assert r.status_code == 400  # la contraseña sola no sube el nivel
    assert spa.post(A + "reautenticar/", {"factor": "totp", "codigo": codigo(secreto)}).status_code == 204
    assert spa.delete(A + "seguridad/totp/").status_code == 204  # desactivar el MFA, con step-up


@pytest.mark.parametrize(
    ("metodo", "ruta", "datos"),
    [
        ("post", "cambiar-password/", {"actual": "clave-segura-123", "nueva": "otra-clave-larga-99"}),
        ("post", "establecer-password/", {"nueva": "otra-clave-larga-99"}),
        ("post", "social/google/vincular/", None),
        ("delete", "acceso/google/", None),
        ("post", "seguridad/totp/", None),
        ("delete", "seguridad/totp/", None),
        ("post", "seguridad/passkeys/reto/", None),
        ("post", "seguridad/passkeys/", {}),
        ("delete", "seguridad/passkeys/1/", None),
    ],
)
def test_las_acciones_sensibles_exigen_una_autenticacion_reciente(time_machine, metodo, ruta, datos):
    spa = entrar(UsuarioFactory())
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=6))
    r = getattr(spa, metodo)(A + ruta, datos)
    assert (r.status_code, r.json()["type"]) == (401, "reautenticacion_requerida")


def test_borrar_un_hogar_exige_una_autenticacion_reciente(time_machine, hogar_con_roles):
    hogar, roles = hogar_con_roles
    spa = entrar(roles["admin"])
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=6))
    assert spa.delete(f"/api/v1/hogares/{hogar.pk}/").status_code == 401
    assert entrar(roles["miembro"]).delete(f"/api/v1/hogares/{hogar.pk}/").status_code == 403  # el rol, antes


# ── Passkeys ──


def test_registrar_una_passkey_y_entrar_sin_contrasena(django_capture_on_commit_callbacks):
    ana = UsuarioFactory()
    autenticador = AutenticadorFalso()
    spa = entrar(ana)
    opciones = spa.post(A + "seguridad/passkeys/reto/").json()
    with django_capture_on_commit_callbacks(execute=True):
        r = spa.post(A + "seguridad/passkeys/", {"respuesta": autenticador.crear(opciones)}, format="json")
    assert r.status_code == 201 and "Has añadido la passkey «Passkey de Chrome en macOS»." in mail.outbox[-1].body
    assert [p["nombre"] for p in spa.get(A + "seguridad/").json()["passkeys"]] == ["Passkey de Chrome en macOS"]

    c = navegador()
    opciones = c.post(A + "passkey/reto/").json()
    assert opciones["allowCredentials"] == [] and opciones["userVerification"] == "required"
    reto = c.cookies["webauthn"]
    assert (reto["path"], reto["httponly"]) == ("/api/v1/auth/passkey/", True)
    r = c.post(A + "passkey/", {"respuesta": autenticador.firmar(opciones)}, format="json")
    assert r.status_code == 200 and r.cookies["refresh"]
    assert Sesion.objects.filter(usuario=ana).latest("creada").factores == ["passkey"]
    c.cookies["webauthn"] = reto.value  # quien la copió: el reto ya no está en el servidor
    r = c.post(A + "passkey/", {"respuesta": autenticador.firmar(opciones)}, format="json")
    assert (r.status_code, r.json()["type"]) == (400, "passkey_no_valida")


def test_una_passkey_como_segundo_factor():
    ana = UsuarioFactory()
    activar_mfa(ana)
    autenticador = AutenticadorFalso()
    opciones = container.empezar_registro_passkey().ejecutar(EmpezarRegistroPasskeyInputDTO(ana.pk, ana.email, "Ana"))
    container.registrar_passkey().ejecutar(RegistrarPasskeyInputDTO(ana.pk, "Llave", autenticador.crear(opciones)))
    c = navegador()
    login(c, ana)
    assert c.get(A + "mfa/").json() == {"factores": ["totp", "passkey", "recuperacion"]}
    opciones = c.post(A + "mfa/reto/").json()
    assert len(opciones["allowCredentials"]) == 1  # solo las suyas
    r = c.post(A + "mfa/", {"factor": "passkey", "respuesta": autenticador.firmar(opciones)}, format="json")
    assert r.status_code == 200
    assert Sesion.objects.filter(usuario=ana).latest("creada").factores == ["contrasena", "passkey"]


# ── Sesiones ──


def test_ver_las_sesiones_y_cerrar_las_demas():
    ana = UsuarioFactory()
    portatil, movil_nav = navegador(CHROME_MAC), navegador(SAFARI_IPHONE)
    portatil = con_access(portatil, login(portatil, ana))
    movil = con_access(movil_nav, login(movil_nav, ana))
    sesiones = portatil.get(A + "sesiones/").json()
    assert {(s["dispositivo"], s["actual"]) for s in sesiones} == {("Chrome en macOS", True), ("Safari en iOS", False)}
    assert all(s["ip"] == "127.0.0.0/24" and s["factores"] == ["contrasena"] for s in sesiones)
    assert portatil.post(A + "sesiones/cerrar-las-demas/").json() == {"cerradas": 1}
    assert movil.get(A + "me/").status_code == 401  # su access, rechazado ya (no a los 10 minutos)
    assert movil_nav.post(A + "refresh/").status_code == 401  # y su refresh no renueva
    assert portatil.get(A + "me/").status_code == 200
    (actual,) = portatil.get(A + "sesiones/").json()
    assert portatil.delete(A + f"sesiones/{actual['sid']}/").status_code == 204  # cerrar la propia: salir
    assert portatil.get(A + "me/").status_code == 401


def test_cerrar_la_sesion_de_otro_no_se_puede():
    ana, luis = UsuarioFactory(), UsuarioFactory()
    entrar(ana)
    sid_de_ana = Sesion.objects.get(usuario=ana).sid
    r = entrar(luis).delete(A + f"sesiones/{sid_de_ana}/")
    assert r.status_code == 404 and Sesion.objects.get(sid=sid_de_ana).cerrada is None


def test_el_refresh_rota_pero_la_sesion_es_la_misma():
    ana = UsuarioFactory()
    c = navegador()
    login(c, ana)
    for _ in range(3):
        assert c.post(A + "refresh/").status_code == 200
    (sesion,) = Sesion.objects.filter(usuario=ana)
    assert sesion.refresh_jti and sesion.ultimo_uso > sesion.creada


def test_un_refresh_reutilizado_cierra_la_sesion(time_machine, django_capture_on_commit_callbacks):
    """RFC 9700 §4.14.2: un refresh ya rotado que vuelve lo tiene alguien más (lo ha copiado). La sesión se cierra:
    ni el ladrón ni el legítimo la renuevan (este vuelve a entrar), y llega un aviso."""
    ana = UsuarioFactory(email="ana@example.com")
    legitimo = navegador()
    login(legitimo, ana)
    robado = legitimo.cookies["refresh"].value
    assert legitimo.post(A + "refresh/").status_code == 200  # rota
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=5))
    ladron = navegador()
    ladron.cookies["refresh"] = robado
    with django_capture_on_commit_callbacks(execute=True):
        assert ladron.post(A + "refresh/").status_code == 401
    assert Sesion.objects.get(usuario=ana).cerrada is not None
    assert legitimo.post(A + "refresh/").status_code == 401
    assert "Hemos cerrado la sesión «Chrome en macOS»" in mail.outbox[-1].body


def test_dos_pestanas_a_la_vez_no_son_una_reutilizacion():
    """Dos pestañas de la SPA arrancan a la vez con la misma cookie: la que llega segunda trae el refresh que la otra
    acaba de rotar. Recibe un access, sin rotar (su navegador ya tiene la cookie nueva), y la sesión sigue."""
    ana = UsuarioFactory()
    pestana = navegador()
    login(pestana, ana)
    anterior = pestana.cookies["refresh"].value
    assert pestana.post(A + "refresh/").status_code == 200
    otra = navegador()
    otra.cookies["refresh"] = anterior
    r = otra.post(A + "refresh/")
    assert r.status_code == 200 and "access" in r.json() and "refresh" not in r.cookies
    assert Sesion.objects.get(usuario=ana).cerrada is None and pestana.post(A + "refresh/").status_code == 200


def test_en_la_base_de_datos_no_hay_refresh_tokens():
    """La sesión recuerda el jti de su refresh vigente, no el token: quien lea la base de datos (o un volcado) no
    tiene con qué renovar ninguna sesión. (Los tokens OAuth del módulo 90 se guardan con hash por lo mismo.)"""
    ana = UsuarioFactory()
    c = navegador()
    login(c, ana)
    c.post(A + "refresh/")
    refresh = c.cookies["refresh"].value
    assert Sesion.objects.get(usuario=ana).refresh_jti == RefreshToken(refresh)["jti"]
    with connection.cursor() as cursor:
        tablas = connection.introspection.table_names(cursor)
        assert not [t for t in tablas if t.startswith("token_blacklist")]
        for tabla in tablas:  # ninguna columna de texto de ninguna tabla contiene el refresh token
            columnas = [
                c.name for c in connection.introspection.get_table_description(cursor, tabla)
                if c.type_code in (25, 1043)  # text, varchar
            ]  # fmt: skip
            for columna in columnas:
                cursor.execute(f'SELECT 1 FROM "{tabla}" WHERE "{columna}" LIKE %s LIMIT 1', [f"%{refresh}%"])
                assert cursor.fetchone() is None, (tabla, columna)


def test_recuperar_la_contrasena_cierra_todas_las_sesiones(django_capture_on_commit_callbacks):
    """Quien recupera la contraseña suele creer que alguien más la tiene: las sesiones abiertas (las suyas y las de
    ese alguien) se cierran, y un email lo cuenta (con el enlace a las aplicaciones conectadas, que se conservan)."""
    ana = UsuarioFactory(email="ana@example.com")
    atacante = navegador()
    login(atacante, ana)
    q = parse_qs(urlsplit(EnlacesDjango().crear(ana.pk, "nueva-password")).query)
    datos = {"uid": q["uid"][0], "token": q["token"][0], "password": "otra-clave-larga-987"}
    with django_capture_on_commit_callbacks(execute=True):
        assert navegador().post(A + "recuperar-password/confirmar/", datos).status_code == 204
    assert atacante.post(A + "refresh/").status_code == 401
    assert not Sesion.objects.filter(usuario=ana, cerrada__isnull=True).exists()
    assert "/aplicaciones" in mail.outbox[-1].body


def test_una_sesion_sin_usarse_caduca(time_machine):
    """Una sesión abandonada no se queda «abierta» para siempre en «Sesiones»: la de la SPA caduca con su refresh (7
    días sin usarse); la del authorization server, con su sesión de Django (SESSION_COOKIE_AGE: 2 semanas)."""
    ana = UsuarioFactory()
    spa = entrar(ana)
    container.iniciar_sesion().ejecutar(IniciarSesionInputDTO(ana.pk, Factor.CONTRASENA, Canal.AUTORIZACION))
    assert len(spa.get(A + "sesiones/").json()) == 2
    time_machine.move_to(datetime.now(UTC) + timedelta(days=8))
    assert [s["canal"] for s in entrar(ana).get(A + "sesiones/").json()] == ["spa", "autorizacion"]  # la nueva
    time_machine.move_to(datetime.now(UTC) + timedelta(days=7))
    assert [s["actual"] for s in entrar(ana).get(A + "sesiones/").json()] == [True]  # 15 días: solo la de ahora


def test_logout_cierra_la_sesion():
    ana = UsuarioFactory()
    c = navegador()
    login(c, ana)
    c.post(A + "logout/")
    assert Sesion.objects.get(usuario=ana).cerrada is not None


# ── Avisos ──


def test_aviso_por_email_al_entrar_desde_un_dispositivo_nuevo(django_capture_on_commit_callbacks):
    ana = UsuarioFactory(email="ana@example.com")
    portatil = navegador(CHROME_MAC)
    with django_capture_on_commit_callbacks(execute=True):
        login(portatil, ana)  # la primera vez: nada que avisar
        dispositivo = portatil.cookies["dispositivo"]
        assert (dispositivo["path"], dispositivo["httponly"], dispositivo["samesite"]) == ("/api/", True, "None")
        login(portatil, ana)  # el mismo navegador (trae su cookie): nada
        assert mail.outbox == []
        login(navegador(SAFARI_IPHONE), ana)
    (aviso,) = mail.outbox
    assert aviso.to == ["ana@example.com"] and aviso.subject == "Nuevo inicio de sesión en tu cuenta de Gastos"
    assert "Safari en iOS (red 127.0.0.0/24)" in aviso.body and "/sesiones" in aviso.body


# ── Ejercicio 2: códigos de recuperación nuevos ──


def test_regenerar_los_codigos_con_step_up(time_machine, django_capture_on_commit_callbacks):
    ana = UsuarioFactory()
    secreto, viejos = activar_mfa(ana)
    c = navegador()
    login(c, ana)
    spa = con_access(navegador(), c.post(A + "mfa/", {"factor": "totp", "codigo": codigo(secreto)}))
    with django_capture_on_commit_callbacks(execute=True):
        nuevos = spa.post(A + "seguridad/recuperacion/").json()["codigos"]
    assert len(nuevos) == 10 and not set(nuevos) & set(viejos)
    assert "Has generado códigos de recuperación nuevos" in mail.outbox[-1].body
    time_machine.move_to(datetime.now(UTC) + timedelta(minutes=6))
    assert spa.post(A + "seguridad/recuperacion/").json()["type"] == "reautenticacion_requerida"
    c = navegador()
    login(c, ana)
    assert c.post(A + "mfa/", {"factor": "recuperacion", "codigo": viejos[0]}).status_code == 400
    assert c.post(A + "mfa/", {"factor": "recuperacion", "codigo": nuevos[0]}).status_code == 200
