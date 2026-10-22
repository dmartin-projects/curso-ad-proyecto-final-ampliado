"""Qué páginas pueden abrir el WebSocket (módulo 86).

Con el frontend en Vercel, la página vive en https://gastos.tudominio.com (o en una preview) y el socket se abre
contra wss://api.gastos.tudominio.com: el Origin ya no coincide con ALLOWED_HOSTS (el host de la API) y
AllowedHostsOriginValidator lo rechazaría. Aquí se permite:

- WS_ORIGENES: orígenes exactos (la web de producción o la de staging);
- las previews de UN proyecto y UN equipo de Vercel, con el formato de sus URLs generadas
  (<proyecto>-<9 letras o cifras>-<equipo>.vercel.app). Nunca "*.vercel.app": cualquiera puede publicar ahí.

Sin nada configurado (desarrollo, E2E, tests), lo de siempre: el host del Origin tiene que estar en
ALLOWED_HOSTS. Los ajustes se leen en cada conexión (no al importar asgi.py): override_settings funciona.
"""

import re

from channels.security.websocket import OriginValidator
from django.conf import settings


def patron_previews() -> re.Pattern | None:
    proyecto, equipo = settings.VERCEL_PREVIEW_PROYECTO, settings.VERCEL_PREVIEW_EQUIPO
    if not (proyecto and equipo):
        return None
    # re.escape: un "." sin escapar en el nombre aceptaría cualquier carácter
    return re.compile(rf"https://{re.escape(proyecto)}-[a-z0-9]{{9}}-{re.escape(equipo)}\.vercel\.app")


def origen_permitido(origen: str) -> bool:
    origen = origen.lower().rstrip("/")
    if origen in (o.lower().rstrip("/") for o in settings.WS_ORIGENES):
        return True
    patron = patron_previews()
    return bool(patron and patron.fullmatch(origen))  # fullmatch: ni prefijos ni sufijos de más


class ValidadorOrigen(OriginValidator):
    """El OriginValidator de Channels, con la lista y el patrón de arriba."""

    def __init__(self, application):
        super().__init__(application, allowed_origins=[])

    def valid_origin(self, parsed_origin):
        if parsed_origin is None:  # sin cabecera Origin: no es un navegador
            return False
        if settings.WS_ORIGENES or patron_previews():
            return origen_permitido(f"{parsed_origin.scheme}://{parsed_origin.netloc}")
        self.allowed_origins = settings.ALLOWED_HOSTS  # sin configurar: como AllowedHostsOriginValidator
        return self.validate_origin(parsed_origin)
