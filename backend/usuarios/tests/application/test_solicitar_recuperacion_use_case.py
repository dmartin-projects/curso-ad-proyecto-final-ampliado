"""SolicitarRecuperacionUseCase y ConfirmarRecuperacionUseCase con fakes (módulo 88): sin Django auth ni base de datos."""

import pytest

from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)
from usuarios.application.solicitar_recuperacion_use_case.dtos.solicitar_recuperacion_input_dto import (
    SolicitarRecuperacionInputDTO,
)
from usuarios.application.solicitar_registro_use_case.dtos.solicitar_registro_input_dto import SolicitarRegistroInputDTO
from usuarios.domain.events.recuperacion_pedida_event import RecuperacionPedidaEvent
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent
from usuarios.domain.exceptions.enlace_no_valido_exception import EnlaceNoValidoException
from usuarios.tests.fakes.mundo import Mundo

CLAVE = "una-clave-muy-larga"


def con_cuenta(mundo: Mundo, email: str = "ana@example.com") -> int:
    """Una cuenta activa, con su contraseña: registrada y completada."""
    pk = mundo.cuentas.crear_pendiente(email=email, nombre="", apellidos="")
    mundo.cuentas.completar_registro(pk, CLAVE)
    return pk


def completar(pk: int) -> RegistroPorCompletarEvent:
    return RegistroPorCompletarEvent(pk, f"https://app/completar-registro?uid={pk}&token=ok")


def test_recuperar_no_revela_que_emails_existen():
    mundo = Mundo()
    mundo.registrar.ejecutar(SolicitarRegistroInputDTO("luis@example.com"))
    luis, ana = mundo.cuentas.por_email("luis@example.com"), con_cuenta(mundo)
    mundo.eventos.publicados.clear()
    mundo.solicitar.ejecutar(SolicitarRecuperacionInputDTO("nadie@example.com"))
    mundo.solicitar.ejecutar(SolicitarRecuperacionInputDTO("esto no es un email"))
    assert mundo.eventos.publicados == []  # y ninguna de las dos llamadas dice nada distinto
    mundo.solicitar.ejecutar(
        SolicitarRecuperacionInputDTO("luis@example.com")
    )  # aún no tiene contraseña que recuperar: el enlace para elegirla
    mundo.solicitar.ejecutar(SolicitarRecuperacionInputDTO("ANA@example.com"))
    assert mundo.eventos.publicados == [
        completar(luis),
        RecuperacionPedidaEvent(ana, f"https://app/nueva-password?uid={ana}&token=ok"),
    ]
    with pytest.raises(EnlaceNoValidoException):
        mundo.confirmar.ejecutar(
            ConfirmarRecuperacionInputDTO(str(luis), "ok", "otra-clave-muy-larga")
        )  # un registro pendiente se completa
    mundo.confirmar.ejecutar(ConfirmarRecuperacionInputDTO(str(ana), "ok", "otra-clave-muy-larga"))
    assert mundo.cuentas.comprobar_contrasena(ana, "otra-clave-muy-larga")
