# asistente/tests/fakes/llm_fake.py — ILLM con guion: un LLM de mentira para tests deterministas (módulo 93)
"""Un LLM real no sirve para un test unitario: tarda, cuesta, necesita red y clave, y no contesta dos veces lo mismo.

LLMFake implementa el MISMO port y devuelve, en orden, los pasos del guion. Además apunta cada petición (es un spy),
para comprobar QUÉ le llegó al modelo: el historial, las tools, si podía llamarlas…

    llm = LLMFake([LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("Gastasteis 812 €.")])
"""

import json
from collections.abc import Callable

from asistente.application.ports.i_llm import ILLM
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.uso import Uso

# Un paso: una respuesta fija, una excepción que lanzar o una función que decide a partir de la petición
Paso = RespuestaLLM | Exception | Callable[[PeticionLLM], RespuestaLLM]


class GuionAgotadoError(AssertionError):
    """El código llamó al LLM más veces de las que el test esperaba."""


class LLMFake(ILLM):
    def __init__(self, guion: list[Paso], modelo: str = "fake"):
        self.guion = list(guion)
        self._modelo = modelo
        self.peticiones: list[PeticionLLM] = []

    @property
    def modelo(self) -> str:
        return self._modelo

    def generar(self, peticion: PeticionLLM) -> RespuestaLLM:
        self.peticiones.append(peticion)
        if not self.guion:
            raise GuionAgotadoError(f"Llamada nº {len(self.peticiones)} al LLM y el guion ya se ha acabado")
        paso = self.guion.pop(0)
        if isinstance(paso, Exception):
            raise paso
        return paso(peticion) if callable(paso) else paso

    # ── Atajos para escribir guiones ──
    @staticmethod
    def responder(texto: str, uso: Uso | None = None, modelo: str = "fake") -> RespuestaLLM:
        return RespuestaLLM(Mensaje.modelo(texto=texto), MotivoFin.FIN, uso or Uso(100, 20), modelo)

    @staticmethod
    def llamar(nombre: str, **argumentos) -> RespuestaLLM:
        """Un turno con UNA tool call."""
        return LLMFake.llamadas((nombre, argumentos))

    @staticmethod
    def llamadas(*llamadas: tuple[str, dict | str]) -> RespuestaLLM:
        """Un turno con varias tool calls: llamadas(("a", {...}), ("b", '{"roto"')). Un str va tal cual: así se
        prueban los argumentos que no son JSON."""
        lista = tuple(
            LlamadaTool(f"fake-{i}", nombre, args if isinstance(args, str) else json.dumps(args))
            for i, (nombre, args) in enumerate(llamadas)
        )
        return RespuestaLLM(Mensaje.modelo(llamadas=lista), MotivoFin.TOOLS, Uso(100, 10), "fake")
