"""Los topics de Kafka de Gastos (módulo 85) y su configuración.

Los crea `manage.py crear_topics` (el broker tiene desactivada la creación automática): así cada topic
nace con sus particiones y su política, y no con los valores por defecto del primer productor que escriba.
"""

MOVIMIENTOS = "gastos.movimientos"
MEMBRESIAS = "gastos.membresias"

# Topics COMPACTADOS: Kafka guarda, para cada clave, al menos el ÚLTIMO mensaje (y borra los anteriores
# poco a poco). Con la clave = id del objeto, el topic es una copia del estado actual de todos los
# objetos: un consumidor nuevo lo lee desde el principio y reconstruye su base de datos entera.
# Un mensaje con valor nulo ("tombstone") dice "este objeto ya no existe"; se borra pasado delete.retention.ms.
COMPACTADO = {
    "cleanup.policy": "compact",
    "min.cleanable.dirty.ratio": "0.1",  # compacta cuando el 10 % del topic son versiones viejas
    "segment.ms": str(24 * 3600 * 1000),  # el segmento activo no se compacta: se cierra cada día
    "delete.retention.ms": str(7 * 24 * 3600 * 1000),  # los tombstones viven 7 días: da tiempo a verlos
}

TOPICS = {
    # 3 particiones: hasta 3 consumidores del mismo grupo leyendo en paralelo. El orden se garantiza
    # DENTRO de una partición; como la clave es el id del movimiento, todas las versiones de un
    # movimiento van a la misma partición y se leen en el orden en que se publicaron.
    MOVIMIENTOS: {"particiones": 3, "config": COMPACTADO},
    MEMBRESIAS: {"particiones": 1, "config": COMPACTADO},
}

ESQUEMA = "1"  # versión del formato de los mensajes; viaja en la cabecera "esquema"
