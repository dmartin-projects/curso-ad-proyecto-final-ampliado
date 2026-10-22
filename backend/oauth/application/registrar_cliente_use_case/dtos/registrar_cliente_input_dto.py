# oauth/application/registrar_cliente_use_case/dtos/registrar_cliente_input_dto.py (módulo 90)
from dataclasses import dataclass, field

from oauth.domain.enums.tipo_cliente import TipoCliente


@dataclass(frozen=True)
class RegistrarClienteInputDTO:
    nombre: str
    tipo: TipoCliente
    scopes: frozenset[str]
    redirect_uris: tuple[str, ...] = field(default=())
    client_id: str | None = None
