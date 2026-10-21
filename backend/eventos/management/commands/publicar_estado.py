"""Publica el estado ACTUAL de todos los movimientos y membresías (módulo 85).

Para la primera vez que se despliega el módulo 85 (los datos anteriores no tienen eventos) y para reparar
una proyección desviada. Repetirlo es inofensivo: los consumidores se quedan con la versión más reciente.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from eventos import registro


class Command(BaseCommand):
    help = "Escribe en el outbox un evento 'instantanea' por cada movimiento y membresía actual."

    def add_arguments(self, parser):
        parser.add_argument("--hogar", type=int, help="Solo este hogar")

    def handle(self, *args, hogar, **opciones):
        with transaction.atomic():
            n = registro.instantanea(hogar_id=hogar)
        self.stdout.write(self.style.SUCCESS(f"{n} eventos al outbox; el relay los publicará"))
