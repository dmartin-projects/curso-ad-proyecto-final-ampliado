"""Abrir una sesión: sin MFA basta el primer factor, y el aviso de dispositivo nuevo (módulo 92)."""

from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.domain.events.inicio_desde_dispositivo_nuevo_event import InicioDesdeDispositivoNuevoEvent
from usuarios.domain.vo.contexto import Contexto
from usuarios.tests.application.escenarios_mfa import entrar
from usuarios.tests.fakes.mundo import Mundo


def test_sin_mfa_la_contrasena_basta():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    sesion = entrar(mundo, luis)
    assert isinstance(sesion, SesionAbiertaOutputDTO) and sesion.autenticacion.acr == "urn:gastos:acr:1fa"


def test_aviso_de_dispositivo_nuevo_solo_cuando_lo_es():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    primera = entrar(mundo, luis, contexto=Contexto("Chrome", "83.45.120.17", ""))  # sin cookie: le da una
    assert primera.dispositivo and not mundo.eventos.de_tipo(InicioDesdeDispositivoNuevoEvent)  # la primera, no
    entrar(mundo, luis, contexto=Contexto("Chrome", "83.45.120.17", primera.dispositivo))
    assert not mundo.eventos.de_tipo(InicioDesdeDispositivoNuevoEvent)  # el mismo navegador
    entrar(mundo, luis, contexto=Contexto("Mozilla/5.0 (iPhone) Safari/604.1", "91.2.3.4", ""))
    (aviso,) = mundo.eventos.de_tipo(InicioDesdeDispositivoNuevoEvent)
    assert (aviso.dispositivo, aviso.ip) == ("Safari en iOS", "91.2.3.0/24")
