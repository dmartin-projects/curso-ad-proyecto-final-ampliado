# oauth/domain/enums/scope.py — lo que una aplicación puede pedir (módulo 90)
#
# Un scope limita lo que una aplicación puede hacer EN NOMBRE de un usuario. No da permisos: el rol del usuario en
# el hogar sigue mandando. Lo que la aplicación puede hacer es la intersección de los dos (Actor.limitado_a).
from enum import StrEnum


class Scope(StrEnum):
    # OpenID Connect: la identidad del usuario (el ID token y /userinfo)
    OPENID = "openid"
    PROFILE = "profile"  # nombre, idioma y zona horaria
    EMAIL = "email"
    # La API de Gastos, en nombre del usuario
    GASTOS_LEER = "gastos:leer"
    GASTOS_ESCRIBIR = "gastos:escribir"
    # Un servicio, en su propio nombre (client credentials): no hay usuario detrás
    OPERACIONES_LEER = "operaciones:leer"
