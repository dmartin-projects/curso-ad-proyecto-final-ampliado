# usuarios/application/entrar_con_passkey_use_case/dtos/entrar_con_passkey_input_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.canal import Canal
from usuarios.domain.vo.contexto import Contexto


@dataclass(frozen=True)
class EntrarConPasskeyInputDTO:
    clave: str | None  # la de la cookie que guarda el reto de este navegador
    respuesta: dict
    canal: Canal = Canal.SPA
    contexto: Contexto = Contexto()
