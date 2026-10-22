# hogares/domain/exceptions/invitacion_no_valida_exception.py (módulos 71 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class InvitacionNoValidaException(DominioException):
    codigo = "invitacion_no_valida"
    status = 400
    mensaje = "La invitación no existe, ha caducado o ya se ha usado."
