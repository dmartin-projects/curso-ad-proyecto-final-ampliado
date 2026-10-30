# asistente/domain/exceptions/adjunto_no_valido_exception.py (módulo 97)
from core.domain.exceptions.validacion_exception import ValidacionException


class AdjuntoNoValidoException(ValidacionException):
    mensaje = "El adjunto tiene que ser una imagen (JPEG, PNG o WebP) o un PDF de hasta 10 MB."
    campo = "archivo"
