# asistente/application/chat/artefactos.py — los artefactos, como datos JSON para la interfaz (módulo 97)
from dataclasses import asdict
from typing import Any

from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico
from asistente.domain.vo.grafico import Grafico


def especificacion_a_datos(e: EspecificacionDeGrafico) -> dict[str, Any]:
    return {"tipo": str(e.tipo), "titulo": e.titulo, "fuente": e.fuente, "argumentos": dict(e.argumentos)}


def grafico_a_datos(g: Grafico) -> dict[str, Any]:
    """Lo que dibuja el chat con Chart.js, y la especificación para fijarlo en el dashboard."""
    return {
        **especificacion_a_datos(g.especificacion),
        "etiquetas": list(g.etiquetas),
        "series": [{"nombre": s.nombre, "valores": list(s.valores)} for s in g.series],
        "unidad": g.unidad,
    }


def archivo_a_datos(a: ArchivoExportado) -> dict[str, Any]:
    return asdict(a)  # la URL no se guarda: caduca. Se pide al almacén cada vez que se enseña
