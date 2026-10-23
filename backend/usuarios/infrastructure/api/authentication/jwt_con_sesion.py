# usuarios/infrastructure/api/authentication/jwt_con_sesion.py — la autenticación JWT de las APIs (módulo 92)
#
# Es lo que esta app ofrece a las demás (como oauth/infrastructure/api/authentication/): la autenticación de las
# sesiones de la SPA (aquí), el step-up (api/permissions/autenticacion_reciente.py) y lo que las páginas del
# authorization server usan de las sesiones (api/sessions/).
from django.core.cache import cache
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from usuarios.infrastructure.database.services.sesiones_orm import clave_cerrada


class JWTConSesion(JWTAuthentication):
    """Un access token dura 10 minutos y no se consulta en la base de datos: si su sesión se cierra (desde «Sesiones»,
    al cambiar la contraseña), su sid queda unos minutos en la caché y aquí se rechaza. Una consulta a Redis, no a
    PostgreSQL, en cada petición."""

    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if (sid := token.get("sid")) and cache.get(clave_cerrada(sid)):
            raise exceptions.AuthenticationFailed("La sesión se ha cerrado.", code="sesion_cerrada")
        return token
