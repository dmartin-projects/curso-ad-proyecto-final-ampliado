# core/infrastructure/database/auditoria_django.py — IAuditoria con el modelo RegistroAuditoria (módulos 17 y 87)
from django.contrib.contenttypes.models import ContentType

from core.application.ports.i_auditoria import IAuditoria
from core.domain.enums.accion import Accion
from core.domain.services.diferencias import diferencias
from core.models import RegistroAuditoria


def _registro(accion: Accion, objeto, usuario_id: int | None, antes) -> RegistroAuditoria:
    app_label, modelo = objeto.tipo.split(".")
    cambios = {}
    if antes is not None and accion != Accion.BORRAR:
        cambios = diferencias(antes.datos_auditables(), objeto.datos_auditables())
    return RegistroAuditoria(
        usuario_id=usuario_id,
        accion=accion,
        content_type=ContentType.objects.get_by_natural_key(app_label, modelo),  # en caché tras la primera
        object_id=str(objeto.id),
        representacion=str(objeto)[:200],
        cambios=cambios,
    )


class AuditoriaDjango(IAuditoria):
    """Apunta un cambio de un BO (no de un modelo de Django) en la misma tabla de siempre."""

    def registrar(self, accion: Accion, objeto, usuario_id: int | None, antes=None) -> None:
        _registro(accion, objeto, usuario_id, antes).save()

    def registrar_varios(self, accion: Accion, objetos, usuario_id: int | None, antes=None) -> None:
        # Recategorizar toca cientos de movimientos de una vez: un INSERT para todos sus registros
        antes = antes or [None] * len(objetos)
        registros = [_registro(accion, o, usuario_id, a) for o, a in zip(objetos, antes, strict=True)]
        RegistroAuditoria.objects.bulk_create(registros, batch_size=1000)
