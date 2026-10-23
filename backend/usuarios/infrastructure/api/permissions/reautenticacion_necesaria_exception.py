# usuarios/infrastructure/api/permissions/reautenticacion_necesaria_exception.py — el reto del step-up (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class ReautenticacionNecesariaException(DominioException):
    """401 con el reto del RFC 9470 (OAuth 2.0 Step Up Authentication Challenge): `insufficient_user_authentication` y
    `max_age`, la antigüedad máxima de la autenticación. La SPA lo reconoce, pide confirmar y repite la petición."""

    codigo = "reautenticacion_requerida"
    status = 401
    mensaje = "Por seguridad, confirma que eres tú para hacer esto."

    def __init__(self, segundos: int):
        super().__init__(max_age=segundos)
        self.cabeceras = {  # (en una cabecera, solo ASCII: la descripción para personas va en el cuerpo, en castellano)
            "WWW-Authenticate": (
                f'Bearer realm="api", error="insufficient_user_authentication", '
                f'error_description="A more recent authentication is required", max_age="{segundos}"'
            )
        }
