"""CambiarContrasenaUseCase con fakes (módulo 88): sin Django auth ni base de datos."""

import pytest

from usuarios.application.cambiar_contrasena_use_case.dtos.cambiar_contrasena_input_dto import CambiarContrasenaInputDTO
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent
from usuarios.domain.exceptions.contrasena_actual_incorrecta_exception import ContrasenaActualIncorrectaException
from usuarios.domain.exceptions.contrasena_no_valida_exception import ContrasenaNoValidaException
from usuarios.tests.fakes.mundo import Mundo

CLAVE = "una-clave-muy-larga"


def con_cuenta(mundo: Mundo, email: str = "ana@example.com") -> int:
    """Una cuenta activa, con su contraseña: registrada y completada."""
    pk = mundo.cuentas.crear_pendiente(email=email, nombre="", apellidos="")
    mundo.cuentas.completar_registro(pk, CLAVE)
    return pk


def completar(pk: int) -> RegistroPorCompletarEvent:
    return RegistroPorCompletarEvent(pk, f"https://app/completar-registro?uid={pk}&token=ok")


def test_cambiar_la_contrasena_cierra_las_demas_sesiones():
    mundo = Mundo()
    pk = con_cuenta(mundo)
    with pytest.raises(ContrasenaActualIncorrectaException):
        mundo.cambiar.ejecutar(CambiarContrasenaInputDTO(pk, "mal", "otra-clave-muy-larga"))
    with pytest.raises(ContrasenaNoValidaException) as e:
        mundo.cambiar.ejecutar(CambiarContrasenaInputDTO(pk, CLAVE, "corta"))
    assert e.value.campo == "nueva" and mundo.sesiones.cerradas == []
    mundo.cambiar.ejecutar(CambiarContrasenaInputDTO(pk, CLAVE, "otra-clave-muy-larga"))
    assert mundo.sesiones.cerradas == [pk]
