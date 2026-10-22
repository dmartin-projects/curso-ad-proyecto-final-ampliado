# oauth/infrastructure/web/views/estado_dispositivo_view.py — "ya puedes volver al dispositivo" (ejercicio 3 del módulo 90)
from oauth2_provider.views import device as dot


class EstadoDispositivoView(dot.DeviceGrantStatusView):
    template_name = "oauth/dispositivo_estado.html"
