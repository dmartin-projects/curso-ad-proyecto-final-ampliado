# oauth/infrastructure/web/views/iniciar_sesion_view.py — el login del authorization server (módulo 90)
#
# Las pantallas del authorization server son páginas de Django (server-side), no de la SPA: quien pide un token es
# OTRA aplicación, y la contraseña solo se escribe en una página del propio Gastos (como en Google o en Auth0
# Universal Login). Si la escribiera en la aplicación cliente, esta la vería: eso es justo lo que OAuth evita.
from django.contrib.auth import views as auth_views
from rest_framework.throttling import ScopedRateThrottle


class IniciarSesionView(auth_views.LoginView):
    template_name = "oauth/login.html"
    redirect_authenticated_user = True
    throttle_scope = "login"  # el mismo límite (y el mismo contador por IP) que el login de la API: 5/min

    def post(self, request, *args, **kwargs):
        if not ScopedRateThrottle().allow_request(request, self):
            contexto = self.get_context_data(form=self.get_form(), demasiados_intentos=True)
            return self.render_to_response(contexto, status=429)
        return super().post(request, *args, **kwargs)
