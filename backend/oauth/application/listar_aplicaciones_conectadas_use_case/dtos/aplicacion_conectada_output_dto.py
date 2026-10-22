# oauth/application/listar_aplicaciones_conectadas_use_case/dtos/aplicacion_conectada_output_dto.py (ejercicio 1 del módulo 90)
from dataclasses import asdict, dataclass
from datetime import datetime

from oauth.domain.read_models.aplicacion_conectada import AplicacionConectada


@dataclass(frozen=True, slots=True)
class AplicacionConectadaOutputDTO:
    client_id: str
    nombre: str
    scopes: tuple[str, ...]
    desde: datetime
    ultimo_uso: datetime

    @classmethod
    def desde_read_model(cls, rm: AplicacionConectada) -> "AplicacionConectadaOutputDTO":
        return cls(**asdict(rm))
