# asistente/domain/vo/uso.py — los tokens de una llamada (o de varias): lo que se paga (módulo 93)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Uso:
    entrada: int = 0  # prompt: instrucciones + historial + declaraciones de tools + resultados
    salida: int = 0  # todo lo generado: la respuesta visible, las tool calls Y el razonamiento
    razonamiento: int = 0  # de la salida, los tokens de razonamiento (no se ven, se pagan)
    cache: int = 0  # de la entrada, los servidos desde la caché del proveedor (prompt caching: más baratos)
    # Ejercicio 1 del 106: de la entrada, los ESCRITOS en la caché (Anthropic los cobra un 25 % más caros; Groq, no)
    cache_escrita: int = 0

    def __add__(self, otro: "Uso") -> "Uso":
        return Uso(
            self.entrada + otro.entrada,
            self.salida + otro.salida,
            self.razonamiento + otro.razonamiento,
            self.cache + otro.cache,
            self.cache_escrita + otro.cache_escrita,
        )

    @property
    def total(self) -> int:
        return self.entrada + self.salida
