"""SolicitarRegistroUseCase con fakes (módulo 88): sin Django auth ni base de datos."""

from usuarios.application.solicitar_recuperacion_use_case.dtos.solicitar_recuperacion_input_dto import (
    SolicitarRecuperacionInputDTO,
)
from usuarios.application.solicitar_registro_use_case.dtos.solicitar_registro_input_dto import SolicitarRegistroInputDTO
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.events.registro_con_cuenta_activa_event import RegistroConCuentaActivaEvent
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent
from usuarios.tests.fakes.mundo import Mundo

CLAVE = "una-clave-muy-larga"


def con_cuenta(mundo: Mundo, email: str = "ana@example.com") -> int:
    """Una cuenta activa, con su contraseña: registrada y completada."""
    pk = mundo.cuentas.crear_pendiente(email=email, nombre="", apellidos="")
    mundo.cuentas.completar_registro(pk, CLAVE)
    return pk


def completar(pk: int) -> RegistroPorCompletarEvent:
    return RegistroPorCompletarEvent(pk, f"https://app/completar-registro?uid={pk}&token=ok")


def test_el_registro_no_dice_si_el_email_tenia_cuenta_se_lo_dice_a_su_dueno():
    mundo = Mundo()
    ana = con_cuenta(mundo)
    for email in ("luis@example.com", "luis@example.com", "ANA@example.com"):
        assert mundo.registrar.ejecutar(SolicitarRegistroInputDTO(email)) is None  # el mismo resultado en los tres
    luis = mundo.cuentas.por_email("luis@example.com")
    assert mundo.eventos.publicados == [
        completar(luis),
        completar(luis),  # registrarse otra vez sin haberlo completado: el mismo correo
        RegistroConCuentaActivaEvent(ana, f"https://app/nueva-password?uid={ana}&token=ok"),
    ]
    assert len(mundo.cuentas.usuarios) == 2 and mundo.cuentas.comprobar_contrasena(ana, CLAVE)  # Ana, igual


def test_una_cuenta_desactivada_no_recibe_enlaces():
    mundo = Mundo()
    ana = con_cuenta(mundo)
    mundo.cuentas.usuarios[ana]["activo"] = False  # la ha desactivado soporte
    mundo.registrar.ejecutar(SolicitarRegistroInputDTO("ana@example.com"))
    mundo.solicitar.ejecutar(SolicitarRecuperacionInputDTO("ana@example.com"))
    assert mundo.eventos.publicados == [] and mundo.cuentas.estado(ana) is EstadoCuenta.DESACTIVADA
