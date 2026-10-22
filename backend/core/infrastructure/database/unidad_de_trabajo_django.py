# core/infrastructure/database/unidad_de_trabajo_django.py — IUnidadDeTrabajo con Django (módulo 87)
from django.db import transaction

from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo


class UnidadDeTrabajoDjango(IUnidadDeTrabajo):
    """`with uow:` es `with transaction.atomic():`. Anidada, un savepoint (como atomic)."""

    def __init__(self):
        self._abiertas = []  # una pila: el mismo use case puede ejecutarse dentro de otro

    def __enter__(self) -> None:
        atomic = transaction.atomic()
        atomic.__enter__()
        self._abiertas.append(atomic)

    def __exit__(self, *excepcion) -> bool | None:
        return self._abiertas.pop().__exit__(*excepcion)
