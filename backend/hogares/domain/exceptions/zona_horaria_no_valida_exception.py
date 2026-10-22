# hogares/domain/exceptions/zona_horaria_no_valida_exception.py (módulos 71 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class ZonaHorariaNoValidaException(ValidacionException):
    campo = "zona_horaria"
    mensaje = "No es una zona horaria válida (por ejemplo, Europe/Madrid)."
