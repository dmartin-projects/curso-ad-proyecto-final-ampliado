# usuarios/application/iniciar_sesion_use_case/dtos/iniciar_sesion_input_dto.py (módulos 35, 91 y 92)
from dataclasses import dataclass

from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.contexto import Contexto


@dataclass(frozen=True)
class IniciarSesionInputDTO:
    usuario_id: int
    factor: Factor  # el primero: CONTRASENA, PROVEEDOR o PASSKEY
    canal: Canal = Canal.SPA  # ejercicio 3 del módulo 91: o la sesión de Django del authorization server
    contexto: Contexto = Contexto()
    volver: str = "/"  # adónde ir tras el segundo paso (la vuelta de un proveedor: una ruta ya comprobada)
    passkey_sincronizada: bool = False
