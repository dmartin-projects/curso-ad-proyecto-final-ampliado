# usuarios/domain/vo/par_de_tokens.py — lo que recibe la SPA al entrar, con contraseña o con un proveedor (módulos 35 y 91)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParDeTokens:
    access: str  # JWT de 10 minutos: la SPA lo guarda en memoria
    refresh: str  # rota en cada uso: va en la cookie HttpOnly que solo viaja a /api/v1/auth/
