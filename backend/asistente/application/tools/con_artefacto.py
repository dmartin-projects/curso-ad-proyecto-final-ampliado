# asistente/application/tools/con_artefacto.py — una tool que, además de contestar al modelo, produce algo (módulo 97)
from dataclasses import dataclass

from asistente.domain.vo.artefacto import Artefacto


@dataclass(frozen=True, slots=True)
class ConArtefacto:
    """Lo que devuelve `ejecutar` cuando hay algo para la INTERFAZ, no para el modelo: un gráfico, un archivo, una
    propuesta. El modelo lee `para_el_modelo`, corto (de un gráfico, un resumen de sus cifras para comentarlo, no los
    puntos); el artefacto va por fuera, al ResultadoAgente y al observador, y el chat lo dibuja. Así el modelo no
    escribe los datos ni los enlaces (podría copiarlos mal, o inventar una URL), y el resultado que se paga en cada
    vuelta sigue siendo pequeño."""

    para_el_modelo: dict
    artefacto: Artefacto
