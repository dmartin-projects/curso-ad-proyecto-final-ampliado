# asistente/application/evals/juez.py — LLM-as-judge: un modelo puntúa lo que el código no puede (módulo 103)
"""Para lo que no se decide con una expresión regular: ¿la respuesta dice que no hay datos en vez de inventarlos? ¿se
entiende? ¿contesta a lo que se preguntó?

Un juez LLM tiene sesgos conocidos, y cada uno tiene su remedio aquí:
- verbosidad (prefiere lo largo): la rúbrica lo dice expresamente;
- auto-preferencia (puntúa mejor lo de su familia): el juez es de OTRA familia que el modelo evaluado (Qwen frente a
  gpt-oss);
- deriva (la misma respuesta, notas distintas): temperatura 0, rúbrica concreta, una referencia con la que comparar y
  una escala con significado para cada número;
- posición (en comparaciones de dos): ejercicio 3, se pregunta en los dos órdenes.
Y se calibra con juicios humanos antes de fiarse de él (ejercicio 2).
"""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, ValidationError

from asistente.application.evals.caso_de_eval import CasoDeEval
from asistente.application.evals.graders import Nota
from asistente.application.ports.i_llm import ILLM
from asistente.application.prompts.juez import JUEZ
from asistente.application.tools.esquema_json import esquema_json
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.uso import Uso

APRUEBA = 4


def _de_1_a_5(n: int) -> int:
    if not 1 <= n <= 5:
        raise ValueError("de 1 a 5")
    return n


class _Veredicto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    razonamiento: str  # primero: el orden de los campos es el orden en que el modelo los escribe
    puntuacion: Annotated[int, AfterValidator(_de_1_a_5)]


ESQUEMA = EsquemaRespuesta("veredicto", esquema_json(_Veredicto))


class JuezLLM:
    def __init__(self, llm: ILLM):
        self.llm = llm
        self.uso = Uso()  # lo que cuesta juzgar: también se mide

    def juzgar(self, caso: CasoDeEval, respuesta: str) -> Nota | None:
        if not caso.rubrica:
            return None
        mensaje = (
            f"<pregunta>{caso.pregunta}</pregunta>\n<rubrica>{caso.rubrica}</rubrica>\n"
            f"<referencia>{caso.referencia or '(sin referencia)'}</referencia>\n<respuesta>{respuesta}</respuesta>"
        )
        peticion = PeticionLLM(
            sistema=JUEZ.rellenar(), mensajes=(Mensaje.usuario(mensaje),), esquema=ESQUEMA, temperatura=0
        )
        try:
            r = self.llm.generar(peticion)
            self.uso += r.uso
            v = _Veredicto.model_validate_json(r.texto)
        except (LLMException, ValidationError) as e:  # sin juez, el caso no aprueba: mejor un falso negativo
            return Nota("juez", False, f"sin veredicto ({type(e).__name__})")
        return Nota("juez", v.puntuacion >= APRUEBA, f"{v.puntuacion}/5: {v.razonamiento}")
