# core/infrastructure/database/auditoria_de_modelos.py — auditar un MODELO de Django (módulos 17, 79 y 88)
#
# Para lo que se queda como CRUD sobre el ORM (los usuarios y las tareas programadas del backoffice, el comando
# `personal`). Los use cases auditan BOs con el port IAuditoria (auditoria_django.py), en la misma tabla.
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict

from core.domain.services.diferencias import diferencias
from core.models import RegistroAuditoria


def registrar(objeto, accion: str, usuario=None, antes: dict | None = None) -> RegistroAuditoria:
    """Guarda qué cambió. Solo se comparan los campos de `antes`: quien pasa uno o dos campos audita esos."""
    cambios = {}
    if antes and accion != RegistroAuditoria.Accion.BORRAR:
        cambios = diferencias(antes, model_to_dict(objeto, fields=list(antes)))  # la misma regla que las entidades
    return RegistroAuditoria.objects.create(
        usuario=usuario if usuario and usuario.is_authenticated else None,
        accion=accion,
        content_type=ContentType.objects.get_for_model(objeto),
        object_id=str(objeto.pk),
        representacion=str(objeto)[:200],
        cambios=cambios,
    )
