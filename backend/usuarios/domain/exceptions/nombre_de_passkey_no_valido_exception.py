# usuarios/domain/exceptions/nombre_de_passkey_no_valido_exception.py — (módulo 92)
from core.domain.exceptions.validacion_exception import ValidacionException


class NombreDePasskeyNoValidoException(ValidacionException):
    campo = "nombre"
    mensaje = "Ponle un nombre de 1 a 60 caracteres."
