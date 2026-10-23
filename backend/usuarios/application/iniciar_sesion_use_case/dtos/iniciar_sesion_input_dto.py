# usuarios/application/iniciar_sesion_use_case/dtos/iniciar_sesion_input_dto.py (módulo 91 y su ejercicio 3)
from dataclasses import dataclass

from usuarios.domain.enums.canal import Canal


@dataclass(frozen=True)
class IniciarSesionInputDTO:
    usuario_id: int
    canal: Canal = Canal.SPA  # ejercicio 3: o la sesión de Django del authorization server
