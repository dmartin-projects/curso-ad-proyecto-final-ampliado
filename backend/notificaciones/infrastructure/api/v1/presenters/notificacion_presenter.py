# notificaciones/infrastructure/api/v1/presenters/notificacion_presenter.py — del OutputDTO a lo que lee el serializer (módulo 88)
from types import SimpleNamespace

from notificaciones.application.shared.dtos.notificacion_listada_output_dto import NotificacionListadaOutputDTO


def presentar(n: NotificacionListadaOutputDTO) -> SimpleNamespace:
    """NotificacionSerializer lee `hogar` como un objeto con pk (es un ModelSerializer)."""
    campos = {c: getattr(n, c) for c in n.__dataclass_fields__ if c != "hogar_id"}
    return SimpleNamespace(pk=n.id, hogar=None if n.hogar_id is None else SimpleNamespace(pk=n.hogar_id), **campos)
