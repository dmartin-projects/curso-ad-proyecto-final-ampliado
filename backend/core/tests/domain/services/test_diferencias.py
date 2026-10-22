"""La regla de la auditoría (módulo 87)."""

from core.domain.services.diferencias import diferencias
from core.domain.vo.dinero import Dinero


def test_diferencias_de_auditoria():
    antes = {"concepto": "Cena", "importe": Dinero("-10"), "password": "x"}
    despues = {"concepto": "Cena de cumpleaños", "importe": Dinero("-10"), "password": "y"}
    assert diferencias(antes, despues) == {"concepto": ["Cena", "Cena de cumpleaños"]}  # nunca la contraseña
