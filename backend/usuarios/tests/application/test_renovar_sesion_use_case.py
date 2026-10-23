"""Renovar una sesión: cerradas, refresh reutilizados y la otra pestaña (módulo 92)."""

import pytest

from usuarios.application.renovar_sesion_use_case.dtos.renovar_sesion_input_dto import RenovarSesionInputDTO
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.sesion_cerrada_exception import SesionCerradaException
from usuarios.tests.application.escenarios_mfa import entrar
from usuarios.tests.fakes.mundo import Mundo


def test_una_sesion_cerrada_no_se_renueva():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    portatil, movil = entrar(mundo, luis), entrar(mundo, luis)
    assert mundo.renovar.ejecutar(RenovarSesionInputDTO(movil.sid, f"jti-{movil.sid}", "jti-2"))  # rota
    assert mundo.sesiones.cerrar_las_demas(luis, portatil.sid) == 1
    with pytest.raises(SesionCerradaException):
        mundo.renovar.ejecutar(RenovarSesionInputDTO(movil.sid, "jti-2", "jti-3"))
    mundo.renovar.ejecutar(RenovarSesionInputDTO(portatil.sid, f"jti-{portatil.sid}", "jti-4"))
    with pytest.raises(SesionCerradaException):  # un refresh sin sid (de antes del módulo 92): a entrar otra vez
        mundo.renovar.ejecutar(RenovarSesionInputDTO("", "jti-4", "jti-5"))


def test_un_refresh_reutilizado_cierra_la_sesion_y_avisa():
    """RFC 9700 §4.14.2: un refresh ya rotado que vuelve lo tiene alguien más. No se sabe quién es quién: la sesión se
    cierra para los dos (el legítimo vuelve a entrar; el ladrón, no puede)."""
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    sesion = entrar(mundo, luis)
    mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, f"jti-{sesion.sid}", "jti-2"))
    mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, "jti-2", "jti-3"))
    with pytest.raises(SesionCerradaException):
        mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, f"jti-{sesion.sid}", "jti-x"))  # el primero, robado
    assert mundo.sesiones.autenticacion(sesion.sid) is None
    with pytest.raises(SesionCerradaException):
        mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, "jti-3", "jti-4"))  # ni el vigente
    assert mundo.eventos.de_tipo(SeguridadCambiadaEvent) == [
        SeguridadCambiadaEvent(luis, "sesion_reutilizada", "Chrome en macOS")
    ]


def test_la_otra_pestana_con_el_anterior_recibe_un_access_sin_rotar():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    sesion = entrar(mundo, luis)
    assert mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, f"jti-{sesion.sid}", "jti-2")) is True
    assert mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, f"jti-{sesion.sid}", "jti-b")) is False  # a la vez
    assert mundo.renovar.ejecutar(RenovarSesionInputDTO(sesion.sid, "jti-2", "jti-3")) is True  # la cadena sigue
    assert not mundo.eventos.de_tipo(SeguridadCambiadaEvent)
