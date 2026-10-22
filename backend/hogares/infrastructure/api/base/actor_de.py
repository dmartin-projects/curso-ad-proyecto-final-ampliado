# hogares/infrastructure/api/base/actor_de.py — quién pide el use case, en el hogar de la URL (módulos 87, 88 y 90)
#
# El ÚNICO sitio de la API que construye el Actor de una petición: así nadie se salta el límite de los scopes.
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.domain.vo.delegacion import Delegacion


def actor_de(request, rol: str) -> Actor:
    """Quién pide el use case: el usuario con su rol en el hogar. Si la petición la hace una aplicación con un token
    OAuth (módulo 90), lo que pueda hacer está además limitado por sus scopes: la intersección de los dos."""
    actor = Actor(usuario_id=request.user.pk, rol=Rol(rol))
    if isinstance(request.auth, Delegacion):
        return actor.limitado_a(request.auth.techo)
    return actor
