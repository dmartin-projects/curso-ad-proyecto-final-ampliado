# asistente/domain/read_models/hogar_del_usuario.py — el hogar sobre el que se pregunta, visto por quien pregunta (módulo 94)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HogarDelUsuario:
    id: int
    nombre: str
    moneda: str
    zona_horaria: str  # "hoy" y "este mes" son los del hogar, no los del servidor
    rol: str  # el rol de quien pregunta en el hogar
