# usuarios/application/ports/i_tokens.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.domain.vo.par_de_tokens import ParDeTokens


class ITokens(ABC):
    @abstractmethod
    def emitir(self, usuario_id: int) -> ParDeTokens:
        """El par de tokens de la SPA (módulo 35). Anota el último login."""
