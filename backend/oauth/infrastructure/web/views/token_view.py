# oauth/infrastructure/web/views/token_view.py — el token endpoint, con la consulta del dispositivo del RFC 8628 (ejercicio 3 del módulo 90)
# y, desde el 104, los errores de recurso (RFC 8707) en JSON
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from oauth2_provider import views as dot
from oauth2_provider.models import get_device_grant_model
from oauthlib.oauth2.rfc8628 import errors as rfc8628

DeviceGrant = get_device_grant_model()


def _error(error) -> JsonResponse:
    return JsonResponse({"error": error.error}, status=error.status_code)


class TokenView(dot.TokenView):
    """El token endpoint de DOT; cambia la consulta del dispositivo y el Content-Type de algunos errores."""

    def post(self, request, *args, **kwargs):
        respuesta = super().post(request, *args, **kwargs)
        # Módulo 104: un error que oauthlib lanza al guardar el token (invalid_target, RFC 8707: un recurso que no se
        # concedió) sale con el cuerpo en JSON pero sin su Content-Type, y RFC 6749 §5.2 lo pide
        if respuesta.status_code >= 400 and respuesta.content.startswith(b"{"):
            respuesta["Content-Type"] = "application/json"
        return respuesta

    def device_flow_token_response(self, request, device_code, *args, **kwargs):
        with transaction.atomic():  # dos consultas a la vez con el mismo device_code: una espera a la otra
            dispositivo = DeviceGrant.objects.select_for_update().filter(device_code=device_code).first()
            if dispositivo is not None and dispositivo.status == DeviceGrant.AUTHORIZATION_PENDING:
                if not dispositivo.is_expired():  # (si ha caducado, lo marca: DOT responde expired_token)
                    if (timezone.now() - dispositivo.last_checked).total_seconds() < dispositivo.interval:
                        dispositivo.save(update_fields=["last_checked"])
                        return _error(rfc8628.SlowDownError())
                    dispositivo.save(update_fields=["last_checked"])  # auto_now: ahora
            respuesta = super().device_flow_token_response(request, device_code, *args, **kwargs)
            if respuesta.status_code == 200:
                dispositivo.status = DeviceGrant.EXPIRED  # canjeado: no vuelve a dar tokens
                dispositivo.save(update_fields=["status"])
            return respuesta
