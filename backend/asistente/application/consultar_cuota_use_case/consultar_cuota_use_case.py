# asistente/application/consultar_cuota_use_case/consultar_cuota_use_case.py (módulo 98)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.consultar_cuota_use_case.dtos.consultar_cuota_input_dto import ConsultarCuotaInputDTO
from asistente.application.consultar_cuota_use_case.i_consultar_cuota_use_case import IConsultarCuotaUseCase
from asistente.application.cuotas.calcular_cuota import calcular_cuota
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.ports.i_tarifas import ITarifas
from asistente.application.shared.dtos.cuota_output_dto import CuotaOutputDTO
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from core.application.ports.i_reloj import IReloj
from core.domain.enums.rol import Rol


class ConsultarCuotaUseCase(IConsultarCuotaUseCase):
    """Para la interfaz (cuánto queda) y para la vista de la pregunta, que contesta 429 ANTES de abrir el stream."""

    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        membresias: IMembresias,
        planes: IPlanDelHogarRepository,
        tarifas: ITarifas,
        consumos: IConsumoQueryService,
        reloj: IReloj,
    ):
        self.membresias, self.planes, self.tarifas, self.consumos, self.reloj = (
            membresias,
            planes,
            tarifas,
            consumos,
            reloj,
        )

    def ejecutar(self, entrada: ConsultarCuotaInputDTO) -> CuotaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        contexto = ContextoPregunta.abrir(
            usuario_id=entrada.actor.usuario_id, hogar_id=entrada.hogar_id, membresias=self.membresias, reloj=self.reloj
        )
        estado = calcular_cuota(
            contexto, self.reloj.ahora(), planes=self.planes, tarifas=self.tarifas, consumos=self.consumos
        )
        return CuotaOutputDTO.desde_estado(estado)
