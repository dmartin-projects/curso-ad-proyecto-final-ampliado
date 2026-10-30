# asistente/infrastructure/hogares/membresias_en_hogares.py — IMembresias con la app hogares (módulos 94 y 97)
#
# Anti-corruption layer: el asistente pregunta en sus palabras ("¿de qué hogar es miembro y con qué rol?") y este
# adapter lo traduce al query service de hogares, que ya resuelve la membresía en una consulta.
from asistente.application.ports.i_membresias import IMembresias
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from asistente.domain.read_models.miembro_del_hogar import MiembroDelHogar
from hogares.application.listar_hogares_use_case.dtos.listar_hogares_input_dto import ListarHogaresInputDTO
from hogares.application.listar_miembros_use_case.dtos.listar_miembros_input_dto import ListarMiembrosInputDTO
from hogares.infrastructure import container as hogares
from hogares.infrastructure.database.repositories.hogar_query_service_orm import HogarQueryServiceORM


class MembresiasEnHogares(IMembresias):
    def hogar_de(self, usuario_id, hogar_id):
        h = HogarQueryServiceORM().detalle(usuario_id, hogar_id)
        if h is None:
            return None
        return HogarDelUsuario(id=h.id, nombre=h.nombre, moneda=h.moneda, zona_horaria=h.zona_horaria, rol=h.mi_rol)

    def hogares_de(self, usuario_id):
        pagina = hogares.listar_hogares().ejecutar(ListarHogaresInputDTO(usuario_id, orden=("nombre",)))
        return tuple(
            HogarDelUsuario(id=h.id, nombre=h.nombre, moneda=h.moneda, zona_horaria=h.zona_horaria, rol=h.mi_rol)
            for h in pagina.results
        )

    def miembros(self, actor, hogar_id):
        leidos = hogares.listar_miembros().ejecutar(ListarMiembrosInputDTO(hogar_id, actor, orden=("creado",)))
        return tuple(MiembroDelHogar(nombre=m.nombre or "(sin nombre)", rol=m.rol) for m in leidos)
