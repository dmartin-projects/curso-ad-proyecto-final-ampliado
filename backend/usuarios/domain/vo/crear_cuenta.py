# usuarios/domain/vo/crear_cuenta.py — lo que se decide a la vuelta del proveedor: una cuenta nueva (módulo 91)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CrearCuenta:
    email: str
    nombre: str
    apellidos: str
