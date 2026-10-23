# usuarios/domain/services/bloqueo_progresivo.py — frenar a quien prueba códigos (módulo 92)
from datetime import timedelta

# ── Frenar a quien prueba códigos ──
# Un código de 6 cifras con ±1 paso de tolerancia acierta 3 de cada millón de intentos. Lo que lo hace seguro es que
# no se puedan hacer millones: 5 intentos por inicio de sesión pendiente (luego, vuelta a la contraseña) y, por cuenta,
# un bloqueo que crece con los fallos seguidos. Y un techo: NIST SP 800-63B-4 (§3.2.2) pide como mucho 100 fallos
# seguidos; después, el segundo factor queda bloqueado hasta que la persona recupere la cuenta (el enlace de
# recuperación a su email, que además cambia la contraseña que el atacante ya tiene).
FALLOS_POR_TRAMO = 5


ESPERA_MAXIMA = timedelta(hours=1)


TECHO_DE_FALLOS = 100


def espera_tras(fallos: int) -> timedelta:
    """0-4 fallos: nada; 5: 1 min; 10: 2 min; 15: 4 min… hasta 1 hora. El exponente se acota ANTES de calcular: con
    2 ** (tramos - 1) sin acotar, a partir de 210 fallos el número no cabe en un timedelta (OverflowError)."""
    tramos = fallos // FALLOS_POR_TRAMO
    return timedelta(0) if tramos <= 0 else min(timedelta(minutes=2 ** min(tramos - 1, 6)), ESPERA_MAXIMA)
