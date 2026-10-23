# usuarios/domain/vo/sesion_abierta.py — una sesión recién abierta (módulo 92)
#
# y, desde el módulo 92, la sesión como algo con nombre: desde dónde, cuándo, con qué factores; y el segundo paso
from dataclasses import dataclass

from usuarios.domain.vo.autenticacion import Autenticacion
from usuarios.domain.vo.par_de_tokens import ParDeTokens


@dataclass(frozen=True, slots=True)
class SesionAbierta:
    sid: str  # el identificador de la sesión: va en el refresh (y en el access) como claim `sid`
    autenticacion: Autenticacion
    tokens: ParDeTokens | None = None  # Canal.SPA; en Canal.AUTORIZACION la sesión es la de Django
    dispositivo: str = ""  # el que hay que dejar en la cookie (nuevo si no traía uno)
