# usuarios/domain/enums/canal.py — dónde se abre una sesión (módulo 91, ejercicio 3)
from enum import StrEnum


class Canal(StrEnum):
    """Ejercicio 3: dónde se abre la sesión. La SPA recibe sus tokens; las páginas del authorization server (módulo 90:
    login y consentimiento) usan la sesión de Django. Las dos pasan por IniciarSesionUseCase."""

    SPA = "spa"
    AUTORIZACION = "autorizacion"
