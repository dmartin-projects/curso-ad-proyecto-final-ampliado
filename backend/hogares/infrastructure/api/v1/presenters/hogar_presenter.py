# hogares/infrastructure/api/v1/presenters/hogar_presenter.py — del OutputDTO a lo que lee el serializer (módulo 88)
from types import SimpleNamespace

from hogares.application.shared.dtos.hogar_listado_output_dto import HogarListadoOutputDTO


def presentar(h: HogarListadoOutputDTO) -> SimpleNamespace:
    return SimpleNamespace(
        pk=h.id,
        id=h.id,
        nombre=h.nombre,
        moneda=h.moneda,
        zona_horaria=h.zona_horaria,
        mi_rol=h.mi_rol,
        num_miembros=h.num_miembros,
        creado=h.creado,
    )
