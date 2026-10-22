# core/infrastructure/storage/huella_archivo.py — el sha256 de un archivo subido (módulos 74, 75 y 88)
import hashlib


def huella_archivo(archivo) -> str:
    """SHA-256 del contenido, leyendo por trozos (no carga el archivo entero en memoria)."""
    h = hashlib.sha256()
    for trozo in archivo.chunks():
        h.update(trozo)
    archivo.seek(0)
    return h.hexdigest()
