# oauth/infrastructure/api/authentication/token_no_valido_exception.py — 401 de un token OAuth que no vale (módulo 90)
from rest_framework import exceptions


class TokenNoValidoException(exceptions.AuthenticationFailed):
    default_detail = "El token de acceso no es válido, ha caducado o se ha revocado."
