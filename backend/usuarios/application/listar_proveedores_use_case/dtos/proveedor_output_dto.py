# usuarios/application/listar_proveedores_use_case/dtos/proveedor_output_dto.py (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProveedorOutputDTO:
    id: str  # "google"
    nombre: str  # "Google"
