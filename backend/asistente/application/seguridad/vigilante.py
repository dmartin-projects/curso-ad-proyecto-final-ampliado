# asistente/application/seguridad/vigilante.py — el clasificador, con su política (módulo 102)
import logging

from asistente.application.ports.i_detector_de_inyeccion import IDetectorDeInyeccion
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException

logger = logging.getLogger(__name__)


class Vigilante:
    """Decide qué hacer con la puntuación de un IDetectorDeInyeccion:

    - por encima del umbral, el texto es sospechoso: quien llama lo retira (no lo lee el modelo) y avisa;
    - si el clasificador NO ESTÁ DISPONIBLE (LLMNoDisponibleException: un 429, un 5xx, sin conexión), se deja pasar
      (fail open) y queda en el log. Es una decisión: el asistente no se cae porque falle una capa, y las demás (el
      Actor de solo lectura, las propuestas que se confirman, la procedencia, la respuesta saneada) no dependen de él.
      Con fail closed, una caída de Groq dejaría sin leer todos los tickets, y la tentación sería apagarlo;
    - cualquier otro fallo (un 4xx, una respuesta que no es una puntuación, un texto demasiado largo para revisarlo
      entero) depende de LA ENTRADA, y la entrada la puede elegir el atacante: un texto hecho para que el clasificador
      conteste 400 pasaría sin revisar. Ahí, fail closed: se trata como sospechoso.
    """

    def __init__(self, detector: IDetectorDeInyeccion, umbral: float = 0.5):
        if not 0 < umbral < 1:
            raise ValueError("El umbral va entre 0 y 1.")
        self.detector, self.umbral = detector, umbral

    def sospechoso(self, texto: str, origen: str) -> float | None:
        """La puntuación si el texto parece una inyección; None si no (o si no se ha podido saber)."""
        if not texto.strip():
            return None
        try:
            puntuacion = self.detector.puntuar(texto)
        except LLMNoDisponibleException:
            logger.warning("Sin clasificador de inyecciones (%s): %s pasa sin revisar", self.detector.modelo, origen)
            return None
        except LLMException as e:
            logger.warning(
                "El clasificador (%s) no ha podido revisar %s (%s): se retira", self.detector.modelo, origen, e
            )
            return 1.0
        if puntuacion < self.umbral:
            return None
        # Sin el texto: puede llevar datos del hogar, y el log lo lee más gente que el chat
        logger.warning(
            "Posible prompt injection en %s (%.3f)",
            origen,
            puntuacion,
            extra={"asistente": {"inyeccion": origen, "puntuacion": round(puntuacion, 3)}},
        )
        return puntuacion
