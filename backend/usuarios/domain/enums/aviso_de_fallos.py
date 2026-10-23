# usuarios/domain/enums/aviso_de_fallos.py — qué contar a la persona cuando falla el segundo factor (módulo 92)
from enum import StrEnum


class AvisoDeFallos(StrEnum):
    """Lo que hay que contar a la persona (por email): quien falla el segundo factor YA tiene su contraseña."""

    INTENTOS = "fallos_segundo_factor"  # los primeros FALLOS_POR_TRAMO fallos seguidos
    BLOQUEO = "segundo_factor_bloqueado"  # el techo: bloqueado hasta recuperar la cuenta
