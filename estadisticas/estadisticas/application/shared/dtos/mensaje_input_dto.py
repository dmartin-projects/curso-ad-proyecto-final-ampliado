# estadisticas/application/shared/dtos/mensaje_input_dto.py — un mensaje de Kafka, SIN Kafka (módulo 89)
#
# Lo reciben ProcesarLoteUseCase y los ports de aparcados y trazas. Los adapters de entrada de Kafka
# (infrastructure/consumer/) convierten cada `confluent_kafka.Message` en uno de estos; los tests los construyen a
# mano. Así los use cases no dependen de la librería de Kafka.
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MensajeInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    topic: str
    particion: int
    offset: int
    clave: str
    valor: bytes | None  # None: tombstone (un borrado)
    marca: datetime  # cuándo se publicó (el timestamp del mensaje)
    cabeceras: dict[str, str] = {}
