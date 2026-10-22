# estadisticas/application/procesar_lote_use_case/dtos/procesar_lote_input_dto.py — lo que llega en un lote
# (módulo 89)
from pydantic import BaseModel, ConfigDict

from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO


class ProcesarLoteInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    mensajes: list[MensajeInputDTO]
