# oauth/infrastructure/web/views/iniciar_sesion_view.py — el login del authorization server (módulos 90 y 91)
#
# Las pantallas del authorization server son páginas de Django (server-side), no de la SPA: quien pide un token es
# OTRA aplicación, y la contraseña solo se escribe en una página del propio Gastos (como en Google o en Auth0
# Universal Login). Si la escribiera en la aplicación cliente, esta la vería: eso es justo lo que OAuth evita.
from urllib.parse import urlencode

from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework.throttling import ScopedRateThrottle

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.infrastructure import container as cuentas

# Módulo 91, ejercicio 3: por qué no se ha podido entrar con un proveedor (la vuelta trae ?error_social=<código>)
ERRORES_SOCIALES = {
    "cuenta_existente": _("Ya hay una cuenta con ese email: entra con tu contraseña."),
    "email_no_verificado": _("Tu cuenta del proveedor no tiene un email verificado."),
    "acceso_cancelado": _("Has cancelado el inicio de sesión."),
    "cuenta_desactivada": _("Esta cuenta está desactivada."),
}


class IniciarSesionView(auth_views.LoginView):
    template_name = "oauth/login.html"
    redirect_authenticated_user = True
    throttle_scope = "login"  # el mismo límite (y el mismo contador por IP) que el login de la API: 5/min

    def post(self, request, *args, **kwargs):
        if not ScopedRateThrottle().allow_request(request, self):
            contexto = self.get_context_data(form=self.get_form(), demasiados_intentos=True)
            return self.render_to_response(contexto, status=429)
        return super().post(request, *args, **kwargs)

    # ── Módulo 91, ejercicio 3: entrar también con un proveedor, y abrir la sesión por el mismo sitio que la SPA ──

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # La vuelta del proveedor vuelve a esta misma petición de autorización (el `next`, ya comprobado por Django)
        para = urlencode({"para": "autorizar", "volver": self.get_redirect_url()})
        contexto["proveedores"] = [
            (p.nombre, reverse("social-entrar", kwargs={"version": "v1", "proveedor": p.id}) + f"?{para}")
            for p in cuentas.listar_proveedores().ejecutar()
        ]
        if codigo := self.request.GET.get("error_social"):
            contexto["error_social"] = ERRORES_SOCIALES.get(codigo, _("No se ha podido entrar con el proveedor."))
        return contexto

    def form_valid(self, form):
        entrada = IniciarSesionInputDTO(form.get_user().pk, Canal.AUTORIZACION)
        cuentas.iniciar_sesion().ejecutar(entrada)  # (el MFA del módulo 92, aquí)
        return super().form_valid(form)
