# usuarios/application/ports/i_politica_de_contrasenas.py (módulo 88)
from abc import ABC, abstractmethod


class IPoliticaDeContrasenas(ABC):
    @abstractmethod
    def incumplimientos(self, password: str, *, usuario_id: int) -> list[str]:
        """Los motivos por los que no vale para esa cuenta (longitud, demasiado común, parecida a su email…).
        Vacía: vale."""
