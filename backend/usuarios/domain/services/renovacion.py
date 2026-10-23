# usuarios/domain/services/renovacion.py — renovar la sesión: el refresh vigente, uno reutilizado y el de otra pestaña (módulo 92)
from datetime import timedelta

from usuarios.domain.enums.estado_renovacion import EstadoRenovacion

# ── Renovar la sesión: el refresh vigente, uno reutilizado y el de otra pestaña ──
# Dos pestañas de la SPA que arrancan a la vez piden su refresh con la misma cookie: una lo rota, la otra llega con el
# anterior un instante después. Eso no es un robo. Un refresh ya rotado que llega más tarde, sí lo parece.
MARGEN_ENTRE_PESTANAS = timedelta(seconds=10)


def clasificar_refresh(*, presentado: str, anterior: str, desde_la_rotacion: timedelta) -> EstadoRenovacion:
    """Un refresh de una sesión abierta que NO es el vigente: ¿la otra pestaña, o alguien que lo ha robado?"""
    if anterior and presentado == anterior and desde_la_rotacion <= MARGEN_ENTRE_PESTANAS:
        return EstadoRenovacion.CONCURRENTE
    return EstadoRenovacion.REUTILIZADA
