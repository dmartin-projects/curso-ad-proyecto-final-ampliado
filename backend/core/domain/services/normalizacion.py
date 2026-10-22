# core/domain/services/normalizacion.py — lógica pura: reconocer "MERCADONA S.A. 1234" como Mercadona (módulos 72, 74 y 88)
#
# Shared kernel: la usan finanzas (reconocer comercios) e importaciones (la huella de cada fila del extracto).
# Las dos TIENEN que normalizar igual: una huella calculada de otra forma no reconocería duplicados.
# (módulos 72, 74 y 87)
import re
import unicodedata

# Ruido típico de conceptos bancarios y tickets (se aplica DESPUÉS de quitar la puntuación)
_RUIDO = re.compile(
    r"\b(s a u|s l u|s a|s l|sau|slu|sa|sl|sociedad|compra|tarj|tarjeta|pago|cargo|recibo|ref|n|\d{4,}|www|com|es)\b"
)


def normalizar(texto: str) -> str:
    """'MERCADONA, S.A. 1234 MADRID' → 'mercadona madrid' (minúsculas, sin acentos, sin ruido)."""
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = _RUIDO.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()
