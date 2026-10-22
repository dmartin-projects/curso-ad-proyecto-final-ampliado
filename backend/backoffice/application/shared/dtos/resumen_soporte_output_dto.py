# backoffice/application/shared/dtos/resumen_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass

from backoffice.application.shared.dtos.por_estado_output_dto import PorEstadoOutputDTO
from backoffice.domain.read_models.resumen_soporte import ResumenSoporte


@dataclass(frozen=True, slots=True)
class ResumenSoporteOutputDTO:
    tickets_24h: tuple[PorEstadoOutputDTO, ...]
    tickets_atascados: int
    importaciones_en_curso: int
    importaciones_con_error_7d: int
    hogares: int
    usuarios_activos: int

    @classmethod
    def desde_read_model(cls, rm: ResumenSoporte) -> "ResumenSoporteOutputDTO":
        return cls(
            tickets_24h=tuple(PorEstadoOutputDTO.desde_read_model(x) for x in rm.tickets_24h),
            tickets_atascados=rm.tickets_atascados,
            importaciones_en_curso=rm.importaciones_en_curso,
            importaciones_con_error_7d=rm.importaciones_con_error_7d,
            hogares=rm.hogares,
            usuarios_activos=rm.usuarios_activos,
        )
