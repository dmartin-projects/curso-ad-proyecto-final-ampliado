# hogares/infrastructure/database/mappers/hogar_mapper.py — BO ↔ fila (módulo 88)
from hogares.domain.bo.hogar import Hogar
from hogares.infrastructure.database.models.hogar_model import Hogar as HogarModel


def hogar_a_bo(fila: HogarModel) -> Hogar:
    return Hogar(id=fila.pk, nombre=fila.nombre, moneda=fila.moneda, zona_horaria=fila.zona_horaria)


def hogar_a_modelo(h: Hogar) -> HogarModel:
    return HogarModel(pk=h.id, nombre=h.nombre, moneda=h.moneda, zona_horaria=h.zona_horaria)
