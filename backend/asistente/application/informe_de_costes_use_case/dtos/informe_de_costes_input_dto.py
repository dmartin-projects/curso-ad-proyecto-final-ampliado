# asistente/application/informe_de_costes_use_case/dtos/informe_de_costes_input_dto.py (módulo 98)
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class InformeDeCostesInputDTO:
    desde: date  # incluido
    hasta: date  # excluido: "octubre" es del 1 de octubre al 1 de noviembre
    por_canal: bool = False  # ejercicio 1: lo que se ve (chat) y lo que no (títulos), por separado
