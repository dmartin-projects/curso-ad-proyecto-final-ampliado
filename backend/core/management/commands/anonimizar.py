"""Staging con datos de producción, sin datos personales (módulo 86, ejercicio 2).

    docker compose run --rm web python manage.py anonimizar --si      # SOLO con ENTORNO=staging en el .env

Lo usa infra/staging-desde-produccion.sh justo después de restaurar en staging la copia de producción.
Quita lo que identifica a alguien (emails, nombres, IBAN, notas, texto de los tickets, notificaciones y
auditoría) y lo que no debe viajar de un entorno a otro (sesiones, refresh tokens, el outbox de eventos y, desde el
módulo 91, las cuentas de Google, GitHub o Apple vinculadas).
Los importes, fechas, categorías y conceptos se quedan: es lo que hace útil probar con datos de verdad.
Todos los usuarios quedan con la misma contraseña (la que diga STAGING_PASSWORD) para poder entrar como ellos.
"""

import os

from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import CharField, F, Value
from django.db.models.functions import Cast, Concat
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from core.models import RegistroAuditoria
from eventos.models import EventoPendiente
from finanzas.models import Cuenta, Movimiento
from hogares.models import Hogar, Invitacion
from notificaciones.models import Notificacion
from tickets.models import Ticket
from usuarios.models import IdentidadExterna, Usuario


def _con_id(prefijo: str, sufijo: str = ""):
    return Concat(Value(prefijo), Cast(F("id"), CharField()), Value(sufijo))


class Command(BaseCommand):
    help = "Anonimiza una copia de producción restaurada en staging (módulo 86)"

    def add_arguments(self, parser):
        parser.add_argument("--si", action="store_true", help="Confirmo que esta base de datos es una COPIA")

    def handle(self, *args, si, **options):
        # La comprobación que importa: el .env del entorno. En producción, este comando no hace nada.
        if (entorno := os.environ.get("ENTORNO")) != "staging":
            raise CommandError(f"Solo en staging (ENTORNO=staging). Aquí ENTORNO={entorno!r}")
        if not si:
            raise CommandError("Sobrescribe datos de todos los usuarios. Para hacerlo: --si")
        clave = os.environ.get("STAGING_PASSWORD")
        if not clave or len(clave) < 12:
            raise CommandError("Falta STAGING_PASSWORD (12 caracteres o más): será la contraseña de todos")

        with transaction.atomic():
            # update() en bloque: sin signals (ni auditoría ni eventos por cada fila) y en segundos
            usuarios = Usuario.objects.update(
                email=_con_id("usuario", "@staging.invalid"), nombre=_con_id("Usuario "), password=make_password(clave)
            )
            Invitacion.objects.update(email=_con_id("invitado", "@staging.invalid"))
            Hogar.objects.update(nombre=_con_id("Hogar "))
            Cuenta.objects.exclude(iban="").update(iban="")
            Movimiento.objects.exclude(notas="").update(notas="")
            Ticket.objects.update(texto_ocr="", datos_ia={}, nombre_original=_con_id("ticket-", ".jpg"))
            borrados = {
                "notificaciones": Notificacion.objects.all().delete()[0],
                "auditoría": RegistroAuditoria.objects.all().delete()[0],
                "sesiones": Session.objects.all().delete()[0],
                "refresh tokens": OutstandingToken.objects.all().delete()[0],  # y su lista negra (CASCADE)
                "outbox": EventoPendiente.objects.all().delete()[0],  # los de producción, publicados o no
                # Módulo 91: su email y su `sub` identifican a la persona; y con ellos, su Google entraría en staging
                "identidades externas": IdentidadExterna.objects.all().delete()[0],
            }
        self.stdout.write(f"{usuarios} usuarios anonimizados; borrado: {borrados}")
        self.stdout.write("Siguiente: publicar_estado (staging tiene topics nuevos) y reconstruir las estadísticas")
