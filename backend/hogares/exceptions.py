from django.utils.translation import gettext_lazy as _

from core.domain.exceptions.dominio_exception import DominioException


class InvitacionNoValida(DominioException):
    codigo = "invitacion_no_valida"
    status = 400
    mensaje = _("La invitación no existe, ha caducado o ya se ha usado.")


class YaEsMiembro(DominioException):
    codigo = "ya_es_miembro"
    mensaje = _("Ya perteneces a este hogar.")


class UltimoAdministrador(DominioException):
    codigo = "ultimo_administrador"
    mensaje = _("Un hogar necesita al menos un administrador.")
