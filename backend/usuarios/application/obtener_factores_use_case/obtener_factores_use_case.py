# usuarios/application/obtener_factores_use_case/obtener_factores_use_case.py — con qué puede completar una cuenta el segundo paso o un step-up (módulo 92)
from usuarios.application.obtener_factores_use_case.dtos.factores_disponibles_output_dto import (
    FactoresDisponiblesOutputDTO,
)
from usuarios.application.obtener_factores_use_case.dtos.obtener_factores_input_dto import ObtenerFactoresInputDTO
from usuarios.application.obtener_factores_use_case.i_obtener_factores_use_case import IObtenerFactoresUseCase
from usuarios.application.shared.factores_de_cuenta import FactoresDeCuenta


class ObtenerFactoresUseCase(IObtenerFactoresUseCase):
    def __init__(self, *, factores: FactoresDeCuenta):
        self.factores = factores

    def ejecutar(self, entrada: ObtenerFactoresInputDTO) -> FactoresDisponiblesOutputDTO:
        return FactoresDisponiblesOutputDTO.desde_vo(self.factores.de(entrada.usuario_id))
