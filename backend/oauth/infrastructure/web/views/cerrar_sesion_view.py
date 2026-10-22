# oauth/infrastructure/web/views/cerrar_sesion_view.py — "¿No eres tú?" en el authorization server (módulo 90)
from django.contrib.auth import views as auth_views


class CerrarSesionView(auth_views.LogoutView):
    """ "¿No eres tú?" en la pantalla de consentimiento: cierra la sesión del authorization server (solo esa: la
    de la SPA es otra) y vuelve al login con la misma petición de autorización."""

    def get_success_url(self):
        return self.get_redirect_url() or "/"
