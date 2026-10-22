# hogares/infrastructure/api/v1/presenters/miembro_presenter.py — del OutputDTO a lo que lee el serializer (módulo 88)
from types import SimpleNamespace

from hogares.application.shared.dtos.miembro_listado_output_dto import MiembroListadoOutputDTO


def presentar(m: MiembroListadoOutputDTO) -> SimpleNamespace:
    # MiembroSerializer lee usuario.email y usuario.get_full_name (un método: DRF lo llama)
    usuario = SimpleNamespace(pk=m.usuario_id, email=m.email, get_full_name=lambda: m.nombre)
    return SimpleNamespace(pk=m.id, id=m.id, usuario=usuario, rol=m.rol, creado=m.creado)
