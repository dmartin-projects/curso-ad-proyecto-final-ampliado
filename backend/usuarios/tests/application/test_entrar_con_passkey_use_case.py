"""Entrar con una passkey, sin contraseña (módulo 92)."""

import pytest

from usuarios.application.entrar_con_passkey_use_case.dtos.entrar_con_passkey_input_dto import EntrarConPasskeyInputDTO
from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.tests.application.escenarios_mfa import con_mfa, firma, registrar_passkey
from usuarios.tests.fakes.mundo import Mundo


def test_entrar_con_una_passkey_sin_contrasena_ni_segundo_paso():
    mundo = Mundo()
    ana = con_mfa(mundo)
    registrar_passkey(mundo, ana, sincronizada=True)
    opciones = mundo.pedir_reto.ejecutar(PedirRetoInputDTO("entrar:navegador"))
    assert mundo.webauthn.pedidos[-1] == {"permitir": [], "uv": True}  # discoverable y con verificación del usuario
    sesion = mundo.entrar_con_passkey.ejecutar(
        EntrarConPasskeyInputDTO("navegador", firma(mundo, opciones, usuario_id=ana))
    )
    assert isinstance(sesion, SesionAbiertaOutputDTO) and sesion.autenticacion.amr == ["mfa", "swk", "user"]


@pytest.mark.parametrize(
    "trampa",
    [
        {"uv": False},  # sin huella ni PIN: solo "algo que tienes"
        {"manija": b"manija-de-otro"},  # el userHandle no es el de la dueña de la credencial
        {"contador": 0},  # el contador retrocede: ¿un clon del autenticador?
        {"firma": "mala"},
    ],
)
def test_una_passkey_que_no_cuadra_no_entra(trampa):
    mundo = Mundo()
    ana = con_mfa(mundo)
    registrar_passkey(mundo, ana)
    mundo.passkeys.filas[1].contador = 5
    opciones = mundo.pedir_reto.ejecutar(PedirRetoInputDTO("entrar:navegador"))
    respuesta = firma(mundo, opciones, contador=6, usuario_id=ana) | trampa
    with pytest.raises(PasskeyNoValidaException):
        mundo.entrar_con_passkey.ejecutar(EntrarConPasskeyInputDTO("navegador", respuesta))


def test_el_reto_de_una_passkey_vale_una_vez():
    mundo = Mundo()
    ana = con_mfa(mundo)
    registrar_passkey(mundo, ana)
    opciones = mundo.pedir_reto.ejecutar(PedirRetoInputDTO("entrar:navegador"))
    mundo.entrar_con_passkey.ejecutar(EntrarConPasskeyInputDTO("navegador", firma(mundo, opciones, usuario_id=ana)))
    with pytest.raises(PasskeyNoValidaException):  # la misma respuesta, otra vez (replay)
        mundo.entrar_con_passkey.ejecutar(
            EntrarConPasskeyInputDTO("navegador", firma(mundo, opciones, contador=2, usuario_id=ana))
        )
