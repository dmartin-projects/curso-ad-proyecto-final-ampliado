# estadisticas/infrastructure/cli/reconstruir_cli.py — el adapter de línea de comandos del use case
# ReconstruirProyeccionUseCase (módulos 85 y 89), como un management command de Django
"""Reconstruir la proyección desde cero (módulo 85): `python -m estadisticas.reconstruir --si`.

Con el consumidor PARADO: olvida hasta dónde había leído el grupo y vacía las tablas; al arrancar, el consumidor
relee los topics desde el principio.
"""

import argparse
import sys

from estadisticas.domain.exceptions.consumidor_activo_exception import ConsumidorActivoException
from estadisticas.infrastructure import container


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--si", action="store_true", help="Confirmo que quiero vaciar la base de datos del servicio")
    if not p.parse_args().si:
        sys.exit("Vacía la base de datos del servicio. Para hacerlo: --si")
    try:
        container.reconstruir_proyeccion().ejecutar()
    except ConsumidorActivoException as e:
        sys.exit(str(e))
    print("Hecho. Arranca el consumidor: leerá los topics desde el principio.")
