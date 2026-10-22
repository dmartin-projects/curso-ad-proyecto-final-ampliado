# hogares/application/obtener_miembro_use_case/obtener_miembro_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from hogares.application.obtener_miembro_use_case.dtos.obtener_miembro_input_dto import ObtenerMiembroInputDTO
from hogares.application.obtener_miembro_use_case.i_obtener_miembro_use_case import IObtenerMiembroUseCase
from hogares.application.shared.dtos.miembro_listado_output_dto import MiembroListadoOutputDTO
from hogares.domain.repositories.i_miembro_query_service import IMiembroQueryService


class ObtenerMiembroUseCase(IObtenerMiembroUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, miembros: IMiembroQueryService):
        self.miembros = miembros

    def ejecutar(self, entrada: ObtenerMiembroInputDTO) -> MiembroListadoOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leido = self.miembros.detalle(entrada.hogar_id, entrada.membresia_id)
        return None if leido is None else MiembroListadoOutputDTO.desde_read_model(leido)
