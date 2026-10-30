# asistente/domain/services/normalizar.py — un texto sin tildes ni mayúsculas, para buscar (módulo 100)
import unicodedata


def sin_tildes(texto: str) -> str:
    """«Común» y «comun» son la misma búsqueda; la ñ se queda (no es una tilde: «año» no es «ano»)."""
    texto = texto.lower().replace("ñ", "\0")
    sin = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return sin.replace("\0", "ñ")
