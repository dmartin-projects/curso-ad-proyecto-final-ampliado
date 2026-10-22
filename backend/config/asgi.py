import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django_asgi_app = get_asgi_application()  # ⚠️ ANTES de importar consumers (carga las apps, módulo 25)

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from notificaciones.middleware import TicketAuthMiddleware  # noqa: E402
from notificaciones.origenes import ValidadorOrigen  # noqa: E402
from notificaciones.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Módulo 86: los orígenes de Vercel (producción, staging y las previews de ESTE proyecto), no ALLOWED_HOSTS
        "websocket": ValidadorOrigen(TicketAuthMiddleware(URLRouter(websocket_urlpatterns))),
    }
)
