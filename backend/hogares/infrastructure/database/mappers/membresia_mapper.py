# hogares/infrastructure/database/mappers/membresia_mapper.py — BO ↔ fila (módulo 88)
from hogares.domain.bo.membresia import Membresia
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


def membresia_a_bo(fila: MembresiaModel) -> Membresia:
    return Membresia(id=fila.pk, hogar_id=fila.hogar_id, usuario_id=fila.usuario_id, rol=fila.rol)


def membresia_a_modelo(m: Membresia) -> MembresiaModel:
    return MembresiaModel(pk=m.id, hogar_id=m.hogar_id, usuario_id=m.usuario_id, rol=m.rol)
