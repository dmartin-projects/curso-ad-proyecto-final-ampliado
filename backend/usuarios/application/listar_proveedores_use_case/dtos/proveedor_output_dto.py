# usuarios/application/listar_proveedores_use_case/dtos/proveedor_output_dto.py (módulos 91 y 92)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProveedorOutputDTO:
    id: str  # "google"
    nombre: str  # "Google"
    reautentica: bool = False  # módulo 92, ej. 3: sirve para el step-up (vuelve a pedir la contraseña y dice cuándo)
