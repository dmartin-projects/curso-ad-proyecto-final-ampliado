# usuarios/application/shared/dtos/par_de_tokens_output_dto.py (módulos 91 y 92)
from dataclasses import dataclass

from usuarios.domain.vo.par_de_tokens import ParDeTokens


@dataclass(frozen=True, slots=True)
class ParDeTokensOutputDTO:
    access: str
    refresh: str
    jti: str = ""  # módulo 92: el del refresh, el vigente de su sesión

    @classmethod
    def desde_vo(cls, tokens: ParDeTokens) -> "ParDeTokensOutputDTO":
        return cls(access=tokens.access, refresh=tokens.refresh, jti=tokens.jti)
