"""Reconstruir la proyección desde cero (módulo 85): `python -m estadisticas.reconstruir --si`.

Con el consumidor PARADO: borra el consumer group en Kafka (se olvidan los offsets) y vacía las tablas. Al
arrancar el consumidor, sin offsets guardados, `auto.offset.reset=earliest` lo pone a leer desde el principio
de los topics compactados, que guardan el último estado de cada movimiento: la base de datos queda igual que
si hubiera estado escuchando desde el primer día.

Para cuando cambias cómo se calcula algo (una tabla nueva, un bug en la proyección) o pierdes la base de datos.
"""

import argparse
import sys

from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient
from sqlalchemy import text

from .ajustes import ajustes
from .bd import motor


class ConsumidorActivo(Exception):
    pass


def reconstruir() -> None:
    a = ajustes()
    admin = AdminClient({"bootstrap.servers": a.kafka_bootstrap_servers})
    try:
        admin.delete_consumer_groups([a.kafka_grupo], request_timeout=15)[a.kafka_grupo].result()
    except KafkaException as e:
        codigo = e.args[0].code()
        if codigo == KafkaError.NON_EMPTY_GROUP:  # Kafka no deja borrar un grupo con consumidores conectados
            raise ConsumidorActivo("Para el consumidor antes de reconstruir") from e
        if codigo != KafkaError.GROUP_ID_NOT_FOUND:  # no existía: nada que olvidar
            raise
    # Después de borrar el grupo, no antes: si hay un consumidor en marcha, ni se toca la base de datos
    with motor().begin() as c:
        c.execute(text("TRUNCATE movimientos, membresias, progreso"))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--si", action="store_true", help="Confirmo que quiero vaciar la base de datos del servicio")
    if not p.parse_args().si:
        sys.exit("Vacía la base de datos del servicio. Para hacerlo: --si")
    try:
        reconstruir()
    except ConsumidorActivo as e:
        sys.exit(str(e))
    print("Hecho. Arranca el consumidor: leerá los topics desde el principio.")


if __name__ == "__main__":
    main()
