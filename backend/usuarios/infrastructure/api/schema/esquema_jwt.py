# usuarios/infrastructure/api/schema/esquema_jwt.py — OpenAPI de JWTConSesion (módulo 92). Se registra al importarlo
# (UsuariosConfig.ready)
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme

from usuarios.infrastructure.api.authentication.jwt_con_sesion import JWTConSesion


class EsquemaJWT(SimpleJWTScheme):
    """OpenAPI: el mismo esquema (jwtAuth) que el JWTAuthentication de simplejwt."""

    target_class = JWTConSesion
