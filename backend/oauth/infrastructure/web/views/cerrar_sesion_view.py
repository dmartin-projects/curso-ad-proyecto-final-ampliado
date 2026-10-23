# oauth/infrastructure/web/views/cerrar_sesion_view.py — "¿No eres tú?" en el authorization server (módulos 90 y 92)
from django.contrib.auth import views as auth_views

from usuarios.infrastructure.api.sessions.sesion_de_django import salir_de_django


class CerrarSesionView(auth_views.LogoutView):
    """ "¿No eres tú?" en la pantalla de consentimiento: cierra la sesión del authorization server (solo esa: la
    de la SPA es otra) y vuelve al login con la misma petición de autorización."""

    def get_success_url(self):
        return self.get_redirect_url() or "/"

    def post(self, request, *args, **kwargs):
        salir_de_django(request)  # módulo 92: con su sesión de Gastos
        return super().post(request, *args, **kwargs)
