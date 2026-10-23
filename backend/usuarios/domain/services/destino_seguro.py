# usuarios/domain/services/destino_seguro.py — adónde se puede volver tras entrar (módulo 91)
from urllib.parse import urlsplit


def destino_seguro(volver: str | None) -> str:
    """La ruta de la SPA a la que volver tras entrar ("/hogares/3/movimientos"). Solo rutas de Gastos: "//otra.com",
    "/\\otra.com", "https://otra.com" o "javascript:…" llevarían fuera (open redirect), y vuelven a "/"."""
    if not volver or len(volver) > 500 or not volver.startswith("/") or volver.startswith(("//", "/\\")):
        return "/"
    if any(c == "\\" or ord(c) < 0x20 or ord(c) == 0x7F for c in volver):  # "\" y caracteres de control
        return "/"
    partes = urlsplit(volver)
    return "/" if partes.scheme or partes.netloc else volver
