# oauth/infrastructure/web/middleware/sesion_vigente.py — la sesión de Django del authorization server sigue a su
# sesión de Gastos (módulo 92)
#
# Al entrar en /api/oauth/login/ se abre una sesión de Gastos (Canal.AUTORIZACION) y su sid queda en la sesión de
# Django. Si se cierra desde «Sesiones» (o al cambiar la contraseña), esta sesión de Django deja de valer en la
# siguiente petición: con ella se podría seguir dando acceso a aplicaciones.
from django.contrib.auth import logout

from usuarios.infrastructure.api.sessions.sesion_de_django import sesion_de_django_vigente

PREFIJO = "/api/oauth/"


class SesionVigente:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(PREFIJO) and request.user.is_authenticated and not sesion_de_django_vigente(request):
            logout(request)  # como si no hubiera entrado: el login, otra vez (y con su segundo factor)
        return self.get_response(request)
