# estadisticas/domain/enums/resultado.py (módulo 89)
from enum import StrEnum


class Resultado(StrEnum):
    """Qué ha pasado con un mensaje: lo que se anota en su span y lo que comprueban los tests."""

    GUARDADO = "guardado"
    BORRADO = "borrado"
    IGNORADO = "ignorado"  # una versión vieja, un duplicado o un topic que no es de este servicio
    APARCADO = "aparcado"  # nunca se podrá aplicar: va al topic de aparcados (dead letter queue)
