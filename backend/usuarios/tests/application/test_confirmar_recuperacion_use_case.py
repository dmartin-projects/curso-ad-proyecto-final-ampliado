"""Recuperar la contraseña cierra todas las sesiones (módulo 92)."""

from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)
from usuarios.domain.enums.canal import Canal
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.tests.application.escenarios_mfa import entrar
from usuarios.tests.fakes.mundo import Mundo


def test_recuperar_la_contrasena_cierra_todas_las_sesiones_y_avisa():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    suya, del_atacante = entrar(mundo, luis), entrar(mundo, luis, canal=Canal.AUTORIZACION)
    mundo.confirmar.ejecutar(ConfirmarRecuperacionInputDTO(str(luis), "ok", "otra-clave-muy-larga"))
    assert mundo.sesiones.autenticacion(suya.sid) is None and mundo.sesiones.autenticacion(del_atacante.sid) is None
    assert SeguridadCambiadaEvent(luis, "contrasena_recuperada") in mundo.eventos.publicados
