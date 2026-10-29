# asistente/domain/vo/plantilla_de_prompt.py — un prompt como código: texto, versión y huella (módulo 96)
import hashlib
import string
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlantillaDePrompt:
    """Un prompt con huecos ({hoy}, {hogar}…) que se rellenan en cada pregunta.

    Es código: va en el repositorio, se revisa en un pull request, tiene versión y tests. La `version` viaja en el log
    de cada pregunta (módulo 98: comparar versiones) y la `huella` (un hash del texto) permite comprobar en un test que
    nadie cambia el texto sin cambiar la versión.
    """

    nombre: str
    version: str
    texto: str

    @property
    def campos(self) -> frozenset[str]:
        return frozenset(campo for _, campo, _, _ in string.Formatter().parse(self.texto) if campo)

    @property
    def huella(self) -> str:
        return hashlib.sha256(self.texto.encode()).hexdigest()[:12]

    def rellenar(self, **valores: object) -> str:
        """Estricto: un hueco sin valor o un valor sin hueco es un error (un prompt con "{hoy}" literal, o un dato que
        se calcula y nadie usa, no llegan a producción)."""
        faltan, sobran = self.campos - valores.keys(), valores.keys() - self.campos
        if faltan or sobran:
            raise ValueError(f"Prompt {self.nombre}: faltan {sorted(faltan)}, sobran {sorted(sobran)}")
        return self.texto.format(**valores)
