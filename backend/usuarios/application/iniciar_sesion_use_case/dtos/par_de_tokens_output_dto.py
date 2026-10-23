# usuarios/application/iniciar_sesion_use_case/dtos/par_de_tokens_output_dto.py (módulo 91)
from dataclasses import dataclass

from usuarios.domain.vo.par_de_tokens import ParDeTokens


@dataclass(frozen=True, slots=True)
class ParDeTokensOutputDTO:
    access: str
    refresh: str

    @classmethod
    def desde_vo(cls, tokens: ParDeTokens) -> "ParDeTokensOutputDTO":
        return cls(access=tokens.access, refresh=tokens.refresh)
