import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django_asgi_app = get_asgi_application()  # ⚠️ ANTES de importar consumers (carga las apps, módulo 25)

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from asistente.infrastructure.api.mcp.aplicacion_mcp import crear_aplicacion_mcp  # noqa: E402
from notificaciones.infrastructure.websocket.middleware import TicketAuthMiddleware  # noqa: E402
from notificaciones.infrastructure.websocket.origenes import ValidadorOrigen  # noqa: E402
from notificaciones.infrastructure.websocket.routing import websocket_urlpatterns  # noqa: E402

mcp = crear_aplicacion_mcp()  # módulo 104: el servidor MCP del asistente


async def http(scope, receive, send):
    """Módulo 104: /api/mcp y su Protected Resource Metadata, al servidor MCP (Starlette, el SDK oficial); lo demás, a
    Django."""
    if mcp.atiende(scope["path"]):
        return await mcp(scope, receive, send)
    return await django_asgi_app(scope, receive, send)


application = ProtocolTypeRouter(
    {
        "http": http,
        # Módulo 86: los orígenes de Vercel (producción, staging y las previews de ESTE proyecto), no ALLOWED_HOSTS
        "websocket": ValidadorOrigen(TicketAuthMiddleware(URLRouter(websocket_urlpatterns))),
    }
)
