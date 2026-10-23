"""Ayudas para los tests del segundo factor de punta a punta en el backend (módulo 92)."""

from datetime import UTC, datetime, timedelta

import pyotp
from rest_framework.test import APIClient

from usuarios.application.confirmar_totp_use_case.dtos.confirmar_totp_input_dto import ConfirmarTotpInputDTO
from usuarios.application.empezar_totp_use_case.dtos.empezar_totp_input_dto import EmpezarTotpInputDTO
from usuarios.infrastructure import container

A = "/api/v1/auth/"
PASSWORD = "clave-segura-123"  # la de UsuarioFactory
CHROME_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141.0 Safari/537.36"
SAFARI_IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"


def activar_mfa(usuario) -> tuple[str, list[str]]:
    """Activa el TOTP como lo haría la persona con su app (el código de hace 30 s, para que el de ahora quede libre).
    Devuelve el secreto (lo que tiene la app) y los códigos de recuperación."""
    alta = container.empezar_totp().ejecutar(EmpezarTotpInputDTO(usuario.pk, usuario.email))
    codigos = container.confirmar_totp().ejecutar(ConfirmarTotpInputDTO(usuario.pk, codigo(alta.secreto, -30)))
    return alta.secreto, codigos


def codigo(secreto: str, desfase: int = 0) -> str:
    """El que enseña la app ahora (o `desfase` segundos antes o después)."""
    return pyotp.TOTP(secreto).at(datetime.now(UTC) + timedelta(seconds=desfase))


def navegador(user_agent=CHROME_MAC) -> APIClient:
    return APIClient(HTTP_USER_AGENT=user_agent)


def login(c: APIClient, usuario, password=PASSWORD):
    return c.post(A + "login/", {"email": usuario.email, "password": password})


def con_access(c: APIClient, respuesta) -> APIClient:
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {respuesta.json()['access']}")
    return c
