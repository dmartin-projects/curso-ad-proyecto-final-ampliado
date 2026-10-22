# estadisticas/application/reconstruir_proyeccion_use_case/reconstruir_proyeccion_use_case.py — reconstruir la
# proyección desde cero (módulo 89; la operación, del módulo 85)
#
# Para cuando cambias cómo se calcula algo (una columna nueva, un cálculo distinto) o pierdes la base de datos: se
# olvida hasta dónde había leído el grupo y se vacían las tablas. Al arrancar, el consumidor relee los topics
# compactados desde el principio y la base de datos queda igual que si hubiera escuchado desde el primer día.
from estadisticas.application.ports.i_grupo_de_consumidores import IGrupoDeConsumidores
from estadisticas.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from estadisticas.application.reconstruir_proyeccion_use_case.i_reconstruir_proyeccion_use_case import (
    IReconstruirProyeccionUseCase,
)
from estadisticas.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from estadisticas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository
from estadisticas.domain.repositories.i_progreso_command_repository import IProgresoCommandRepository


class ReconstruirProyeccionUseCase(IReconstruirProyeccionUseCase):
    def __init__(
        self,
        *,
        grupo: IGrupoDeConsumidores,
        uow: IUnidadDeTrabajo,
        movimientos: IMovimientoCommandRepository,
        membresias: IMembresiaCommandRepository,
        progreso: IProgresoCommandRepository,
    ):
        self.grupo = grupo
        self.uow = uow
        self.movimientos = movimientos
        self.membresias = membresias
        self.progreso = progreso

    def ejecutar(self) -> None:
        # PRIMERO el grupo: si hay un consumidor conectado, ConsumidorActivoException y la base de datos ni se toca
        self.grupo.olvidar()
        with self.uow:
            self.movimientos.vaciar()
            self.membresias.vaciar()
            self.progreso.vaciar()
