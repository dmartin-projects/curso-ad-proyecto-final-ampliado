# asistente/management/commands/interruptor_asistente.py — apagar el asistente sin reiniciar (ejercicio 1 del 107)
"""manage.py interruptor_asistente apagar --minutos 30 | encender | estado

En Redis (la caché de Django): lo ven a la vez todos los procesos (web, workers) sin reiniciar nada. Con caducidad:
un apagado de emergencia que nadie recuerda deshacer no deja el asistente apagado para siempre. ASISTENTE_ACTIVO=false
(el entorno) sigue mandando: es el apagado "de verdad", el que sobrevive a un reinicio."""

from datetime import timedelta

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from asistente.infrastructure.estado.estado_desde_ajustes_y_circuitos import APAGADO_HASTA


class Command(BaseCommand):
    help = "Apaga el asistente unos minutos (sin reiniciar), lo enciende o dice cómo está."

    def add_arguments(self, parser):
        parser.add_argument("accion", choices=["apagar", "encender", "estado"])
        parser.add_argument("--minutos", type=int, default=30)

    def handle(self, *args, accion, minutos, **options):
        if accion == "apagar":
            hasta = timezone.now() + timedelta(minutes=minutos)
            cache.set(APAGADO_HASTA, hasta.isoformat(), timeout=minutos * 60)
            self.stdout.write(f"Asistente apagado hasta {hasta:%H:%M} UTC.")
        elif accion == "encender":
            cache.delete(APAGADO_HASTA)
            self.stdout.write("Asistente encendido (si ASISTENTE_ACTIVO lo permite).")
        else:
            hasta = cache.get(APAGADO_HASTA)
            self.stdout.write(f"Apagado hasta {hasta}." if hasta else "Sin apagado temporal.")
