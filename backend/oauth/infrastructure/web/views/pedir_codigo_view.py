# oauth/infrastructure/web/views/pedir_codigo_view.py — device authorization grant, RFC 8628 (ejercicio 3 del módulo 90)
#
# Para lo que no tiene navegador (o no uno cómodo): el CLI en un servidor por SSH, una tele. El dispositivo pide un
# device_code y un user_code (esta view); la persona abre /device/ en su móvil u ordenador, escribe el user_code y da
# permiso (introducir_codigo_view.py, confirmar_dispositivo_view.py); mientras, el dispositivo pregunta al token
# endpoint cada `interval` segundos hasta que hay respuesta (token_view.py).
#
# django-oauth-toolkit 3.4 lo trae; aquí se completa en tres cosas que el RFC pide o recomienda y él no hace:
#   - el cliente y los scopes, al PEDIR el código: DOT da un código a cualquier cliente con cualquier scope y no los
#     comprueba hasta canjearlo (la persona vería y aprobaría algo que no se concede, o el nombre de otra app);
#   - slow_down (§3.5) si el dispositivo pregunta más deprisa que `interval`, y expired_token al caducar;
#   - un device_code da UN par de tokens: después, como caducado (DOT lo canjearía otra vez en cada consulta).
from django.http import JsonResponse
from oauth2_provider.models import get_application_model
from oauth2_provider.views import device as dot

from oauth.infrastructure.server.scopes_por_cliente import ScopesPorCliente

Application = get_application_model()


class PedirCodigoView(dot.DeviceAuthorizationView):
    """POST /device-authorization/ (lo llama el dispositivo): device_code, user_code y adónde ir."""

    def post(self, request, *args, **kwargs):
        aplicacion = Application.objects.filter(client_id=request.POST.get("client_id", "")).first()
        if aplicacion is not None:
            if not aplicacion.allows_grant_type(Application.GRANT_DEVICE_CODE):
                return JsonResponse({"error": "unauthorized_client"}, status=400)  # RFC 6749 §5.2
            pedidos = set(request.POST.get("scope", "").split())
            if not pedidos or not pedidos <= set(ScopesPorCliente().get_available_scopes(application=aplicacion)):
                return JsonResponse({"error": "invalid_scope"}, status=400)
        return super().post(request, *args, **kwargs)
