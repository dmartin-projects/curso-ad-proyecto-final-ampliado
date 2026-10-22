"""CompletarRegistroUseCase (tras SolicitarRegistroUseCase) con fakes (módulo 88): sin Django auth ni base de datos."""

import pytest

from usuarios.application.completar_registro_use_case.dtos.completar_registro_input_dto import CompletarRegistroInputDTO
from usuarios.application.solicitar_registro_use_case.dtos.solicitar_registro_input_dto import SolicitarRegistroInputDTO
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent
from usuarios.domain.exceptions.contrasena_no_valida_exception import ContrasenaNoValidaException
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


def test_registro_sin_contrasena_hasta_completarlo_con_el_enlace():
    mundo = Mundo()
    mundo.registrar.ejecutar(SolicitarRegistroInputDTO(" Ana@Example.com", "Ana"))
    pk = mundo.cuentas.por_email("ana@example.com")
    ana = mundo.cuentas.usuarios[pk]
    assert (ana["email"], ana["nombre"], ana["password"], ana["activo"]) == ("ana@example.com", "Ana", None, False)
    assert mundo.eventos.publicados == [completar(pk)]
    with pytest.raises(EnlaceNoValidoException):
        mundo.completar_registro.ejecutar(CompletarRegistroInputDTO(str(pk), "falso", CLAVE))
    with pytest.raises(ContrasenaNoValidaException) as e:
        mundo.completar_registro.ejecutar(CompletarRegistroInputDTO(str(pk), "ok", "corta"))
    assert e.value.campo == "password" and mundo.cuentas.estado(pk) is EstadoCuenta.PENDIENTE  # nada guardado
    mundo.completar_registro.ejecutar(CompletarRegistroInputDTO(str(pk), "ok", CLAVE))
    assert mundo.cuentas.estado(pk) is EstadoCuenta.ACTIVA and mundo.cuentas.comprobar_contrasena(pk, CLAVE)
    with pytest.raises(EnlaceNoValidoException):  # solo completa registros pendientes
        mundo.completar_registro.ejecutar(CompletarRegistroInputDTO(str(pk), "ok", "otra-clave-muy-larga"))
