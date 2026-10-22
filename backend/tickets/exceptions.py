from django.utils.translation import gettext_lazy as _

from core.domain.exceptions.dominio_exception import DominioException


class EstadoNoPermitido(DominioException):
    codigo = "ticket_estado_no_permitido"
    mensaje = _("El ticket no está en un estado que permita esta operación.")
