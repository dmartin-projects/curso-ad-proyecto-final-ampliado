# usuarios/domain/services/dispositivos.py — desde dónde entra alguien, para que lo reconozca (módulo 92)
import ipaddress
import re


def describir_dispositivo(user_agent: str) -> str:
    """'Mozilla/5.0 (Macintosh; …) Chrome/141…' → 'Chrome en macOS'. Para que la persona reconozca sus sesiones,
    no para identificar a nadie: el user agent lo escribe el navegador y se puede falsificar."""
    ua = user_agent or ""
    navegador = next(
        (n for patron, n in (("Edg/", "Edge"), ("OPR/", "Opera"), ("Firefox/", "Firefox"), ("Chrome/", "Chrome"),
                             ("Safari/", "Safari")) if patron in ua),
        "Navegador",
    )  # fmt: skip
    sistema = next(
        (s for patron, s in ((r"iPhone|iPad", "iOS"), (r"Android", "Android"), (r"Windows", "Windows"),
                             (r"Mac OS X|Macintosh", "macOS"), (r"CrOS", "ChromeOS"), (r"Linux", "Linux"))
         if re.search(patron, ua)),
        None,
    )  # fmt: skip
    return f"{navegador} en {sistema}" if sistema else navegador


def ip_aproximada(ip: str) -> str:
    """La red, no la máquina: /24 en IPv4 y /48 en IPv6. Basta para reconocer "es mi casa" y no guarda la IP exacta
    de nadie (minimización de datos, RGPD)."""
    try:
        direccion = ipaddress.ip_address(ip)
    except ValueError:
        return ""
    prefijo = 24 if direccion.version == 4 else 48
    return str(ipaddress.ip_network(f"{direccion}/{prefijo}", strict=False))


def es_dispositivo_nuevo(*, conocido: bool, sesiones_anteriores: int) -> bool:
    """¿Avisar por email? Si este navegador no ha abierto nunca una sesión de esta cuenta… y la cuenta tiene alguna
    (la primera vez que alguien entra en su cuenta nueva no hay nada de lo que avisar)."""
    return not conocido and sesiones_anteriores > 0
