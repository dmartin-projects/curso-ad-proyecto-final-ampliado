# asistente/domain/read_models/coste_por_hogar.py — el informe de costes: un hogar con un modelo (módulo 98)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CostePorHogar:
    hogar_id: int | None  # None: un hogar que ya no existe (su gasto se queda: el dinero se gastó)
    hogar: str
    modelo: str
    llamadas: int  # filas apuntadas: una por pregunta y modelo (y una por título)
    tokens_entrada: int
    tokens_cache: int
    tokens_salida: int
    coste: Decimal  # lo conocido; los modelos sin precio no suman (ver sin_precio)
    sin_precio: int  # llamadas de modelos sin precio en la tabla
    canal: str = ""  # ejercicio 1: con --por-canal, "chat" o "titulo" (sin él, todos juntos)
