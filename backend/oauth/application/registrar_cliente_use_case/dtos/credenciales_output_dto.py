# oauth/application/registrar_cliente_use_case/dtos/credenciales_output_dto.py (módulo 90)
from dataclasses import dataclass

from oauth.domain.vo.credenciales import Credenciales


@dataclass(frozen=True, slots=True)
class CredencialesOutputDTO:
    client_id: str
    client_secret: str | None  # solo los confidenciales: se enseña una vez

    @classmethod
    def desde_vo(cls, credenciales: Credenciales) -> "CredencialesOutputDTO":
        return cls(client_id=credenciales.client_id, client_secret=credenciales.client_secret)
