# oauth/infrastructure/web/views/confirmar_dispositivo_view.py — dar (o no) acceso al dispositivo (ejercicio 3 del módulo 90)
from oauth2_provider.views import device as dot


class ConfirmarDispositivoView(dot.DeviceConfirmView):
    template_name = "oauth/dispositivo_confirmar.html"
