from django.utils.translation import gettext_lazy as _

from core.domain.exceptions.dominio_exception import DominioException


class EnlaceNoValido(DominioException):
    codigo = "enlace_no_valido"
    status = 400
    mensaje = _("Enlace no válido o caducado.")
