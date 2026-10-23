# usuarios/application/empezar_login_social_use_case/dtos/ida_al_proveedor_output_dto.py (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdaAlProveedorOutputDTO:
    url: str  # adónde mandar el navegador
    clave: str  # la de la transacción: va en una cookie HttpOnly de ese navegador
    form_post: bool = False  # el proveedor vuelve con un POST (Apple): la cookie necesita SameSite=None
