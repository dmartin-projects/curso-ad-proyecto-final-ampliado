# asistente/infrastructure/llm/detector_con_politica.py — un clasificador que razona con TU política (ejercicio 3 del 102)
"""IDetectorDeInyeccion con `openai/gpt-oss-safeguard-20b` en Groq: un modelo de razonamiento entrenado para clasificar
contenido según una política que le das tú (en las instrucciones), y no según una lista fija de ataques.

Frente a Prompt Guard 2: entiende las inyecciones indirectas y educadas ("Asistente: cuando te pregunten, di que…"),
que no se parecen a un jailbreak; a cambio, es un LLM (más lento, más caro y con su cuota por minuto) y su respuesta
es una decisión (0 o 1), no una probabilidad.
"""

import json

import openai
from openai import OpenAI

from asistente.application.ports.i_detector_de_inyeccion import IDetectorDeInyeccion
from asistente.application.prompts.politica_inyeccion import POLITICA_INYECCION
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException

# Su ventana es de 131.072 tokens: cabe de sobra lo que lee el modelo de una tool (6.000 caracteres y el aviso) o de un
# adjunto. Un texto más largo no se revisa a medias: PeticionLLMException, y el Vigilante lo retira
MAX_TEXTO = 8000


class DetectorConPolitica(IDetectorDeInyeccion):
    def __init__(self, *, cliente: OpenAI, modelo: str = "openai/gpt-oss-safeguard-20b"):
        self.cliente, self._modelo = cliente, modelo

    @property
    def modelo(self) -> str:
        return self._modelo

    def puntuar(self, texto: str) -> float:
        if len(texto) > MAX_TEXTO:
            raise PeticionLLMException(f"{self._modelo}: {len(texto)} caracteres, más de {MAX_TEXTO}")
        try:
            r = self.cliente.chat.completions.create(
                model=self._modelo,
                messages=[
                    {"role": "system", "content": POLITICA_INYECCION.rellenar()},  # fija: el prefijo que se cachea
                    {"role": "user", "content": texto},
                ],
                response_format={"type": "json_object"},
                reasoning_effort="low",  # una clasificación sencilla: poco razonamiento, menos tokens
                temperature=0,
            )
        except openai.RateLimitError as e:
            raise LLMNoDisponibleException(f"{self._modelo}: 429") from e
        except openai.APIStatusError as e:
            if e.status_code >= 500:
                raise LLMNoDisponibleException(f"{self._modelo}: {e.status_code}") from e
            raise PeticionLLMException(f"{self._modelo}: {e.status_code}") from e
        except openai.APIConnectionError as e:
            raise LLMNoDisponibleException(f"{self._modelo}: sin conexión") from e
        try:
            return float(json.loads(r.choices[0].message.content or "")["violation"])
        except (ValueError, KeyError, TypeError) as e:
            raise LLMException(f"{self._modelo} no ha devuelto la decisión en JSON") from e
