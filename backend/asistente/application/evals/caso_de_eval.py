# asistente/application/evals/caso_de_eval.py — una pregunta del golden set y lo que se espera (módulo 103)
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CasoDeEval:
    """Lo que tiene que cumplir la respuesta a una pregunta sobre la casa de los tests (fakes/casa.py).

    Cada campo es un grader distinto (graders.py): solo se comprueba lo que el caso dice. Lo que no se puede decidir
    con código (¿la respuesta es honesta, se entiende, no inventa?) va en la `rubrica`, para el juez (juez.py).
    """

    id: str
    pregunta: str
    categoria: str  # "cifras", "comparar", "buscar", "fuera", "accion"… para ver por grupos dónde falla
    cifras: tuple[str, ...] = ()  # importes que tienen que aparecer ("776,59"), compárense como números
    contiene: tuple[str, ...] = ()  # expresiones regulares que tiene que cumplir el texto
    no_contiene: tuple[str, ...] = ()  # expresiones regulares que NO puede cumplir
    tools: tuple[str, ...] = ()  # la trayectoria: tools que tiene que llamar (todas, en cualquier orden)
    alguna_de: tuple[str, ...] = ()  # …o al menos una de estas (hay varias formas buenas de contestar)
    prohibidas: tuple[str, ...] = ()  # tools que no puede llamar
    sin_tools: bool = False  # no tiene que llamar a ninguna (una pregunta fuera de su terreno)
    max_vueltas: int | None = None
    rubrica: str = ""  # para el juez: qué es una buena respuesta, en una o dos frases
    referencia: str = ""  # una respuesta buena, para el juez (comparar con algo es más fiable que puntuar en el aire)
    etiquetas: tuple[str, ...] = field(default=())

    @classmethod
    def de_dict(cls, d: dict) -> "CasoDeEval":
        tuplas = ("cifras", "contiene", "no_contiene", "tools", "alguna_de", "prohibidas", "etiquetas")
        return cls(**{k: tuple(v) if k in tuplas else v for k, v in d.items()})
