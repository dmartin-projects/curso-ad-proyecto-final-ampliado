# oauth/infrastructure/web/views/iniciar_sesion_view.py — el login del authorization server (módulos 90, 91 y 92)
#
# Las pantallas del authorization server son páginas de Django (server-side), no de la SPA: quien pide un token es
# OTRA aplicación, y la contraseña solo se escribe en una página del propio Gastos (como en Google o en Auth0
# Universal Login). Si la escribiera en la aplicación cliente, esta la vería: eso es justo lo que OAuth evita.
from urllib.parse import urlencode

from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework.throttling import ScopedRateThrottle

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container as cuentas
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.sessions.sesion_de_django import PENDIENTE_DJANGO, entrar_en_django

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
        # La contraseña es buena: ahora, lo mismo que en la SPA (cuenta activa, segundo factor), en IniciarSesionUseCase
        usuario_id = form.get_user().pk
        entrada = IniciarSesionInputDTO(usuario_id, Factor.CONTRASENA, Canal.AUTORIZACION, contexto_de(self.request))
        resultado = cuentas.iniciar_sesion().ejecutar(entrada)
        if isinstance(
            resultado, SegundoFactorPendienteOutputDTO
        ):  # módulo 92: sin sesión todavía; la clave, en la de Django
            self.request.session[PENDIENTE_DJANGO] = resultado.clave
            return HttpResponseRedirect(
                f"{reverse('oauth2_provider:segundo-factor')}?{urlencode({'next': self.get_success_url()})}"
            )
        entrar_en_django(self.request, resultado, usuario_id)  # login() + cómo se autenticó (para el ID token)
        return HttpResponseRedirect(self.get_success_url())
