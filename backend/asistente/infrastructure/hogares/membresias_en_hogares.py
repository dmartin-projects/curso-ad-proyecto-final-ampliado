# asistente/infrastructure/hogares/membresias_en_hogares.py — IMembresias con la app hogares (módulo 94)
#
# Anti-corruption layer: el asistente pregunta en sus palabras ("¿de qué hogar es miembro y con qué rol?") y este
# adapter lo traduce al query service de hogares, que ya resuelve la membresía en una consulta.
from asistente.application.ports.i_membresias import IMembresias
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from hogares.infrastructure.database.repositories.hogar_query_service_orm import HogarQueryServiceORM


class MembresiasEnHogares(IMembresias):
    def hogar_de(self, usuario_id, hogar_id):
        h = HogarQueryServiceORM().detalle(usuario_id, hogar_id)
        if h is None:
            return None
        return HogarDelUsuario(id=h.id, nombre=h.nombre, moneda=h.moneda, zona_horaria=h.zona_horaria, rol=h.mi_rol)
