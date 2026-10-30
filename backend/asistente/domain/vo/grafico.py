# asistente/domain/vo/grafico.py — un gráfico ya calculado, listo para dibujar (módulo 97)
from dataclasses import dataclass

from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico


@dataclass(frozen=True, slots=True)
class Serie:
    nombre: str
    valores: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class Grafico:
    """La especificación y sus datos: una etiqueta por punto y una o varias series, con un valor por etiqueta."""

    especificacion: EspecificacionDeGrafico
    etiquetas: tuple[str, ...]
    series: tuple[Serie, ...]
    unidad: str = "€"

    def __post_init__(self):
        if any(len(s.valores) != len(self.etiquetas) for s in self.series):
            raise ValueError("Cada serie lleva un valor por etiqueta.")

    def resumen(self) -> dict:
        """Lo justo para comentar el gráfico sin verlo: de qué etiqueta a cuál y, por serie, el total, el máximo, el
        mínimo y el último punto, ya calculados (el modelo no suma ni busca: lee). Son los mismos pocos números con 3
        puntos que con 24, porque el resultado de una tool se paga en cada vuelta."""

        def punto(valores: tuple[float, ...], i: int) -> dict[str, float]:
            return {self.etiquetas[i]: round(valores[i], 2)}

        series = []
        for s in self.series:
            v = s.valores
            series.append(
                {
                    "nombre": s.nombre,
                    "total": round(sum(v), 2),
                    "maximo": punto(v, v.index(max(v))),
                    "minimo": punto(v, v.index(min(v))),
                    "ultimo": punto(v, len(v) - 1),
                }
            )
        return {
            "puntos": len(self.etiquetas),
            "desde": self.etiquetas[0],
            "hasta": self.etiquetas[-1],
            "series": series,
        }
