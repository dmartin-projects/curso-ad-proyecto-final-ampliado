# asistente/domain/enums/tipo_grafico.py — cómo se dibuja un gráfico del chat (módulo 97)
from enum import StrEnum


class TipoGrafico(StrEnum):
    BARRAS = "barras"  # comparar categorías o meses
    LINEAS = "lineas"  # una evolución en el tiempo
    CIRCULAR = "circular"  # el reparto de un total (una sola serie)
