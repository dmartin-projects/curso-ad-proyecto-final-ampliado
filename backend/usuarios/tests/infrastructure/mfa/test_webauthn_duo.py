"""El adapter de WebAuthn (py_webauthn) contra un autenticador en software (módulo 92): cada comprobación, su test."""

import pytest

from usuarios.domain.bo.passkey import Passkey
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.infrastructure.mfa.webauthn_duo import WebAuthnDuo
from usuarios.tests.infrastructure.autenticador_falso import AutenticadorFalso, b64

webauthn = WebAuthnDuo()


def registrar(autenticador: AutenticadorFalso, **trampas) -> Passkey:
    reto = webauthn.opciones_de_registro(manija=b"m" * 32, cuenta="ana@example.com", nombre="Ana", excluir=[])
    nueva = webauthn.comprobar_registro(autenticador.crear(reto.opciones, **trampas), reto.challenge)
    return Passkey(1, nueva.credencial_id, nueva.clave_publica, nueva.contador, "Portátil", nueva.sincronizada)


def entrar(autenticador, passkey, *, exigir_verificacion=True, **trampas):
    reto = webauthn.opciones_de_entrada(permitir=[], exigir_verificacion=exigir_verificacion)
    respuesta = autenticador.firmar(reto.opciones, **trampas)
    return webauthn.comprobar_entrada(respuesta, reto.challenge, passkey, exigir_verificacion=exigir_verificacion)


def test_las_opciones_de_registro_piden_una_passkey_de_verdad(settings):
    settings.FRONTEND_URL = "https://gastos.example"
    reto = webauthn.opciones_de_registro(manija=b"m" * 32, cuenta="ana@example.com", nombre="Ana", excluir=[b"vieja"])
    o = reto.opciones
    assert o["rp"] == {"name": "Gastos", "id": "gastos.example"}  # el rp_id: el dominio de la app en este entorno
    assert o["user"] == {"id": b64(b"m" * 32), "name": "ana@example.com", "displayName": "Ana"}
    assert o["authenticatorSelection"]["residentKey"] == "required"  # discoverable: se entra sin escribir el email
    assert o["authenticatorSelection"]["userVerification"] == "required"
    assert o["attestation"] == "none" and o["excludeCredentials"] == [{"id": b64(b"vieja"), "type": "public-key"}]
    assert len(reto.challenge) >= 32  # 64 bytes aleatorios por defecto


def test_registrar_y_entrar():
    autenticador = AutenticadorFalso()
    passkey = registrar(autenticador)
    assert (passkey.contador, passkey.sincronizada) == (0, False)
    assert entrar(autenticador, passkey).contador == 1


def test_una_passkey_sincronizada_lleva_backup_state_y_contador_cero():
    autenticador = AutenticadorFalso(sincroniza=True, cuenta_firmas=False)
    passkey = registrar(autenticador)
    assert passkey.sincronizada
    assert entrar(autenticador, passkey).contador == 0
    assert entrar(autenticador, passkey).contador == 0  # 0 y 0: no hay contador que comparar (iCloud, Google)


@pytest.mark.parametrize(
    "trampa",
    [
        {"origen": "https://gastos-falso.example"},  # phishing: la web de al lado no puede usar la passkey
        {"rp_id": "otro.example"},  # una passkey de otro sitio
    ],
)
def test_el_registro_comprueba_origen_y_rp_id(trampa):
    with pytest.raises(PasskeyNoValidaException):
        registrar(AutenticadorFalso(), **trampa)


def test_el_registro_exige_verificacion_del_usuario():
    with pytest.raises(PasskeyNoValidaException):
        registrar(AutenticadorFalso(verifica_usuario=False))


def test_el_reto_tiene_que_ser_el_que_se_dio():
    autenticador = AutenticadorFalso()
    passkey = registrar(autenticador)
    reto, otro = (webauthn.opciones_de_entrada(permitir=[], exigir_verificacion=True) for _ in range(2))
    with pytest.raises(PasskeyNoValidaException):
        webauthn.comprobar_entrada(
            autenticador.firmar(otro.opciones), reto.challenge, passkey, exigir_verificacion=True
        )


def test_la_entrada_comprueba_el_origen():
    autenticador = AutenticadorFalso()
    passkey = registrar(autenticador)
    with pytest.raises(PasskeyNoValidaException):
        entrar(autenticador, passkey, origen="https://gastos-falso.example")


def test_la_firma_es_de_la_clave_guardada():
    autenticador, otro = AutenticadorFalso(), AutenticadorFalso()
    passkey = registrar(autenticador)
    registrar(otro)
    with pytest.raises(PasskeyNoValidaException):  # firmada por otra clave, presentada como esta credencial
        entrar(otro, passkey, credencial=otro.credenciales[0])


def test_sin_verificacion_del_usuario_no_entra_sin_contrasena():
    autenticador = AutenticadorFalso()
    passkey = registrar(autenticador)
    autenticador.verifica_usuario = False
    with pytest.raises(PasskeyNoValidaException):
        entrar(autenticador, passkey)
    assert entrar(autenticador, passkey, exigir_verificacion=False).contador == 2  # como segundo factor, sí


def test_un_contador_que_no_avanza_es_un_clon():
    autenticador = AutenticadorFalso()
    passkey = registrar(autenticador)
    passkey.contador = entrar(autenticador, passkey).contador
    with pytest.raises(PasskeyNoValidaException):
        entrar(autenticador, passkey, contador=passkey.contador)  # el mismo: otra copia de la clave lo ha usado


def test_una_respuesta_rota_no_es_un_500():
    with pytest.raises(PasskeyNoValidaException):
        webauthn.credencial({})
    for basura in ({"rawId": "AAAA", "response": "x"}, {"id": "AAAA", "rawId": "AAAA", "response": {}}):
        with pytest.raises(PasskeyNoValidaException):
            webauthn.comprobar_entrada(basura, b"reto", Passkey(1, b"x", b"y", 0, "z"), exigir_verificacion=True)
