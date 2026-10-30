# asistente/domain/read_models/pasaje_encontrado.py — un trozo de la ayuda que encaja con una pregunta (módulo 100)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PasajeEncontrado:
    clave: str
    fuente: str  # documento#sección: lo que se cita
    titulo: str
    texto: str
    puntuacion: float  # de su búsqueda (similitud del coseno o ts_rank): solo sirve para ordenar dentro de ella
