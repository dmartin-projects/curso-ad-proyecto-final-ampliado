# oauth/infrastructure/web/views/introducir_codigo_view.py — /device/: escribir el código del dispositivo (ejercicio 3 del módulo 90)
from oauth2_provider.views import device as dot
from rest_framework.throttling import ScopedRateThrottle


class IntroducirCodigoView(dot.DeviceUserCodeView):
    """/device/: la persona, ya con su sesión del authorization server, escribe el código que ve en el dispositivo."""

    template_name = "oauth/dispositivo_codigo.html"
    throttle_scope = "login"  # 40 bits de user_code, pero sin límite se podrían probar códigos sin parar

    def post(self, request, *args, **kwargs):
        if not ScopedRateThrottle().allow_request(request, self):
            return self.render_to_response(self.get_context_data(demasiados_intentos=True), status=429)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "data" in kwargs:  # "abcd-efgh" o "ABCD EFGH" es el mismo código que ABCDEFGH (como lo enseña el CLI)
            datos = kwargs["data"].copy()
            datos["user_code"] = datos.get("user_code", "").upper().replace("-", "").replace(" ", "")
            kwargs["data"] = datos
        return kwargs
