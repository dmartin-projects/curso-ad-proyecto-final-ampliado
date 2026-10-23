# usuarios/domain/exceptions/ultimo_metodo_de_acceso_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class UltimoMetodoDeAccesoException(DominioException):
    codigo = "ultimo_metodo_de_acceso"
    status = 409
    mensaje = "Es tu única forma de entrar: establece una contraseña o vincula otro proveedor antes de quitarla."
