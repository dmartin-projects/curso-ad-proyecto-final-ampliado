# estadisticas/application/procesar_lote_use_case/dtos/procesar_lote_input_dto.py — lo que llega en un lote
# (módulo 89)
from pydantic import BaseModel, ConfigDict

from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO


class ProcesarLoteInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    mensajes: list[MensajeInputDTO]
    # Ejercicio 1: False para mensajes que no vienen de la cabeza del topic (los aparcados que se reintentan);
    # anotar su offset haría retroceder el progreso de su partición
    anotar_progreso: bool = True
