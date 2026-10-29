# asistente/domain/services/grupos_ecoicop.py — de una categoría de Gastos a su grupo del IPC (módulo 95)
"""El IPC no se publica por "Supermercado" sino por grupos de la clasificación COICOP 2018 (la que usa Eurostat desde
2026; el INE publica el mismo IPC armonizado de España). Las categorías de Gastos las pone cada hogar, así que la
traducción es explícita, por nombre, y probada: las categorías por defecto (módulo 72) y unos sinónimos. Lo que no
está aquí se compara con el IPC general, y se dice.
"""

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GrupoEcoicop:
    codigo: str  # el código de Eurostat: "CP011", "TOTAL"…
    nombre: str  # en castellano, para el modelo
    exacto: bool  # False: no hay grupo para esa categoría y es el IPC general


GENERAL = GrupoEcoicop("TOTAL", "IPC general", exacto=False)
_GRUPOS = {
    ("supermercado", "alimentacion", "comida", "compra"): ("CP011", "Alimentos"),
    ("hogar", "casa", "vivienda"): ("CP04", "Vivienda, agua, electricidad, gas y otros combustibles"),
    ("alquiler / hipoteca", "alquiler"): ("CP041", "Alquiler de vivienda"),
    ("luz", "electricidad"): ("CP0451", "Electricidad"),
    ("agua",): ("CP0441", "Suministro de agua"),
    ("gas",): ("CP0452", "Gas"),
    ("internet y movil", "telefono", "internet", "movil"): ("CP083", "Servicios de información y comunicación"),
    ("transporte",): ("CP07", "Transporte"),
    ("combustible", "gasolina"): ("CP0722", "Carburantes y lubricantes"),
    ("transporte publico",): ("CP073", "Servicios de transporte de pasajeros"),
    ("parking",): ("CP072", "Uso de vehículos personales"),
    ("restaurantes", "bares", "restauracion"): ("CP111", "Restaurantes, cafeterías y bares"),
    ("salud",): ("CP06", "Salud"),
    ("farmacia",): ("CP061", "Medicamentos y productos sanitarios"),
    ("ocio", "suscripciones", "cultura"): ("CP09", "Ocio, deporte y cultura"),
    ("viajes",): ("CP098", "Paquetes turísticos"),
    ("ropa",): ("CP03", "Vestido y calzado"),
    ("educacion",): ("CP10", "Educación"),
}
_POR_NOMBRE = {nombre: grupo for nombres, grupo in _GRUPOS.items() for nombre in nombres}


def _clave(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower().strip()


def grupo_de(categoria: str, padre: str | None = None) -> GrupoEcoicop:
    """El grupo de la categoría; si no tiene, el de su categoría principal; si tampoco, el IPC general."""
    for nombre in (categoria, padre):
        if nombre and (encontrado := _POR_NOMBRE.get(_clave(nombre))):
            return GrupoEcoicop(*encontrado, exacto=True)
    return GENERAL
