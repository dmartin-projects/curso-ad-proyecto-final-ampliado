# core/infrastructure/database/guardado.py — lo que comparten los command repositories del ORM (módulo 87)
#
# El use case no comprueba "¿existe ya?" antes de guardar (dos peticiones a la vez pasarían las dos la
# comprobación); guarda, y si PostgreSQL dice que no, el repositorio traduce la constraint a un error del dominio.
from django.db import IntegrityError, transaction


def nombre_constraint(error: IntegrityError) -> str | None:
    """El nombre de la constraint que ha saltado, sin leer el mensaje (psycopg lo da en `diag`)."""
    return getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)


def guardar_fila(fila, campos: list[str], errores: dict[str, type[Exception]]) -> None:
    """INSERT si no tiene id; UPDATE de `campos` si lo tiene. En un savepoint: si salta una constraint conocida,
    error del dominio y la transacción del use case sigue viva (sin savepoint, PostgreSQL la daría por rota)."""
    try:
        with transaction.atomic():
            if fila.pk is None:
                fila.save(force_insert=True)
            else:
                fila.save(update_fields=[*campos, "actualizado"])  # "actualizado": auto_now solo si se incluye
    except IntegrityError as e:
        if (error := errores.get(nombre_constraint(e))) is not None:
            raise error() from e
        raise
