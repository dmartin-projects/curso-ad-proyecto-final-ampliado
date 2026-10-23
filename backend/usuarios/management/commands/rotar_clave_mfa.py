"""Vuelve a cifrar todos los secretos TOTP con la primera clave de MFA_CLAVES (módulo 92, docs/runbook.md).

1. MFA_CLAVES=nueva,vieja y despliega: lo nuevo se cifra con la nueva; lo viejo se sigue descifrando con la vieja.
2. manage.py rotar_clave_mfa: todo pasa a la nueva (una fila cada vez: se puede repetir si se corta).
3. MFA_CLAVES=nueva y despliega.
"""

from django.core.management.base import BaseCommand

from usuarios.infrastructure.database.cifrado import recifrar
from usuarios.models import SegundoFactor


class Command(BaseCommand):
    help = "Vuelve a cifrar los secretos TOTP con la clave nueva (módulo 92)"

    def handle(self, *args, **options):
        filas = SegundoFactor.objects.exclude(secreto="")
        for fila in filas.iterator():
            SegundoFactor.objects.filter(pk=fila.pk).update(secreto=recifrar(fila.secreto))
        self.stdout.write(f"{filas.count()} secretos cifrados con la clave nueva")
