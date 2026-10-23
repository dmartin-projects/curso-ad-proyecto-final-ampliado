"""La espera tras los fallos del segundo factor (módulo 92), sin base de datos."""

from datetime import timedelta

from usuarios.domain.services.bloqueo_progresivo import ESPERA_MAXIMA, espera_tras


def test_espera_tras_no_desborda_con_ningun_numero_de_fallos():
    """Test de propiedad: para CUALQUIER número de fallos, espera_tras no lanza, nunca pasa del máximo y nunca baja
    al fallar más. Exhaustivo hasta 100 000 (mucho más de lo que deja el techo) y con números absurdos después."""
    anterior = timedelta(0)
    for n in [*range(100_000), *(10**k for k in range(5, 19)), 2**63 - 1]:
        espera = espera_tras(n)
        assert timedelta(0) <= espera <= ESPERA_MAXIMA and espera >= anterior, n
        anterior = espera
