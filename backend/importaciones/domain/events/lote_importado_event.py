# importaciones/domain/events/lote_importado_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class LoteImportadoEvent:
    importacion_id: int  # → mover la barra de progreso de quien esté mirando
