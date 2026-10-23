# usuarios/application/ports/i_tokens.py (módulos 91 y 92)
from abc import ABC, abstractmethod

from usuarios.domain.vo.par_de_tokens import ParDeTokens


class ITokens(ABC):
    @abstractmethod
    def emitir(self, usuario_id: int, sid: str) -> ParDeTokens:
        """El par de tokens de la SPA (módulo 35), con el sid de su sesión (y el jti del refresh). Anota el último
        login."""
        ...
