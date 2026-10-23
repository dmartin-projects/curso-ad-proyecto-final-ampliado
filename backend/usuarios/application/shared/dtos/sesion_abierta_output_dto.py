# usuarios/application/shared/dtos/sesion_abierta_output_dto.py — una sesión recién abierta (módulo 92)
from dataclasses import dataclass

from usuarios.application.shared.dtos.autenticacion_output_dto import AutenticacionOutputDTO
from usuarios.application.shared.dtos.par_de_tokens_output_dto import ParDeTokensOutputDTO
from usuarios.domain.vo.sesion_abierta import SesionAbierta


@dataclass(frozen=True)
class SesionAbiertaOutputDTO:
    sid: str  # va en el refresh (y en el access) como claim `sid`
    autenticacion: AutenticacionOutputDTO
    tokens: ParDeTokensOutputDTO | None  # Canal.SPA; en Canal.AUTORIZACION la sesión es la de Django
    dispositivo: str  # el que hay que dejar en la cookie (nuevo si no traía uno)

    @classmethod
    def desde_vo(cls, sesion: SesionAbierta) -> "SesionAbiertaOutputDTO":
        return cls(
            sid=sesion.sid,
            autenticacion=AutenticacionOutputDTO.desde_vo(sesion.autenticacion),
            tokens=ParDeTokensOutputDTO.desde_vo(sesion.tokens) if sesion.tokens is not None else None,
            dispositivo=sesion.dispositivo,
        )
