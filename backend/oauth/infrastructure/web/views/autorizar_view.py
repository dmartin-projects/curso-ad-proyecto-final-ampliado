# oauth/infrastructure/web/views/autorizar_view.py — /authorize: la pantalla de consentimiento (módulo 90)
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.contrib.auth import logout
from django.contrib.auth.views import redirect_to_login
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import get_application_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views import AuthorizationView

# Lo que la URL de /authorize no puede decidir, o que ya se ha cumplido al volver del login
NO_VUELVEN_AL_AUTHORIZE = ("approval_prompt", "prompt", "max_age")


class AutorizarView(AuthorizationView):
    """El endpoint /authorize de django-oauth-toolkit, con la plantilla de Gastos y dos reglas más:

    - Volver a pedir la contraseña cuando el cliente lo pide (`prompt=login`) o cuando la autenticación del navegador
      es más antigua de lo que admite (`max_age`): OIDC Core §3.1.2.1 dice que el servidor DEBE hacerlo, no solo
      contarlo en `auth_time`. Antes se cierra la sesión: el login de Gastos devuelve aquí, sin preguntar, a quien ya
      la tiene (redirect_authenticated_user).
    - El consentimiento lo decide el servidor, no la URL.
    """

    template_name = "oauth/autorizar.html"

    def get(self, request, *args, **kwargs):
        # DOT lee `approval_prompt` de la URL ("auto": sin pantalla si ya hay un token vivo con esos scopes). Quien
        # hace la URL no decide si se pregunta: se quita y manda REQUEST_APPROVAL_PROMPT ("force": siempre)
        if "approval_prompt" in request.GET:
            request.GET = request.GET.copy()
            del request.GET["approval_prompt"]
        if (respuesta := self.reautenticacion(request)) is not None:
            return respuesta
        return super().get(request, *args, **kwargs)

    def handle_no_permission(self):
        """Sin sesión: al login, y a la vuelta, sin `prompt` ni `max_age` (la autenticación será la de ahora). Con
        `prompt=none` (el cliente no quiere pantallas), el error `login_required` en su redirect URI."""
        prompt = set(self.request.GET.get("prompt", "").split())
        if "none" in prompt:
            return self.error_oidc(self.request, "login_required")
        if "create" in prompt:  # Gastos no lo anuncia (prompt_values_supported): lo que haga DOT
            return super().handle_no_permission()
        return self.volver_a_entrar(self.request)

    def autenticado_en(self, request) -> datetime | None:
        """Cuándo demostró quién es la sesión de este navegador: el `auth_time` de su ID token."""
        return request.user.last_login

    def reautenticacion(self, request):
        """None si la sesión vale para esta petición; si no, la respuesta: al login (sin la sesión de ahora) o, con
        `prompt=none`, un error en la redirect URI del cliente."""
        prompt = set(request.GET.get("prompt", "").split())
        max_age = request.GET.get("max_age")
        if max_age is not None and not max_age.isdigit():
            return self.error_oidc(request, "invalid_request")  # un número de segundos (≥ 0), nada más
        autenticado_en = self.autenticado_en(request)
        caducada = max_age is not None and (
            autenticado_en is None or (timezone.now() - autenticado_en).total_seconds() > int(max_age)
        )
        if "none" in prompt:
            # Sin pantallas no se puede volver a entrar (login_required) ni consentir: Gastos pregunta siempre
            # (REQUEST_APPROVAL_PROMPT), así que una sesión válida tampoco basta (consent_required)
            return self.error_oidc(request, "login_required" if caducada else "consent_required")
        if "login" in prompt or caducada:
            return self.volver_a_entrar(request)
        return None

    def volver_a_entrar(self, request):
        """Cierra la sesión de este navegador (si no, el login lo devolvería aquí sin pedir nada) y manda al login.
        Al volver, la misma petición sin `prompt` ni `max_age`: la autenticación que piden ya es la de ahora."""
        logout(request)
        consulta = [
            (k, v) for k, v in parse_qsl(request.META.get("QUERY_STRING", "")) if k not in NO_VUELVEN_AL_AUTHORIZE
        ]
        return redirect_to_login(f"{request.path}?{urlencode(consulta)}", self.get_login_url())

    def error_oidc(self, request, error: str):
        """El error, en la redirect URI del cliente (OIDC Core §3.1.2.6). Solo si el cliente existe y esa redirect URI
        es suya: si no, aquí, sin redirigir (un error mandado a una URI cualquiera sería un open redirect)."""
        aplicacion = get_application_model().objects.filter(client_id=request.GET.get("client_id", "")).first()
        redirect_uri = request.GET.get("redirect_uri", "")
        if aplicacion is None or not redirect_uri or not aplicacion.redirect_uri_allowed(redirect_uri):
            fallo = {
                "error": "invalid_request",
                "description": _("La aplicación o su dirección de vuelta no es válida."),
            }
            return self.render_to_response({"error": fallo}, status=400)
        parametros = {"error": error} | ({"state": request.GET["state"]} if request.GET.get("state") else {})
        separador = "&" if "?" in redirect_uri else "?"
        return self.redirect(redirect_uri + separador + urlencode(parametros), aplicacion)

    def redirect(self, redirect_to, application):
        """La vuelta al cliente lleva siempre `iss` (RFC 9207 §2): DOT 3.4 lo pone en las respuestas con code, pero
        no en las de error (access_denied, invalid_scope…), y un cliente que lo comprueba las rechazaría."""
        partes = urlsplit(redirect_to)
        parametros = parse_qsl(partes.query)
        if not any(clave == "iss" for clave, _ in parametros):
            parametros.append(("iss", oauth2_settings.oidc_issuer(self.request)))
            redirect_to = urlunsplit(partes._replace(query=urlencode(parametros)))
        return super().redirect(redirect_to, application)
