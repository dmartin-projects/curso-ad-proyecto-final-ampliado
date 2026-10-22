"""IGrupoDeConsumidores en memoria (módulo 89)."""

from estadisticas.application.ports.i_grupo_de_consumidores import IGrupoDeConsumidores
from estadisticas.domain.exceptions.consumidor_activo_exception import ConsumidorActivoException


class GrupoDeConsumidoresFake(IGrupoDeConsumidores):
    def __init__(self, *, con_consumidores: bool = False):
        self.con_consumidores = con_consumidores
        self.olvidado = False

    def olvidar(self) -> None:
        if self.con_consumidores:
            raise ConsumidorActivoException("Para el consumidor antes de reconstruir")
        self.olvidado = True
