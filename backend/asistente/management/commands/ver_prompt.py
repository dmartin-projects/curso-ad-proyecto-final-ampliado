# asistente/management/commands/ver_prompt.py — el system prompt tal como lo recibe el modelo (módulo 96, ejercicio 2)
"""manage.py ver_prompt --email … --hogar … [--ahora 2027-01-15T12:00] — sin llamar al modelo: lo que vería, cuánto
ocupa y qué versión es. Para revisar un cambio del prompt antes de grabar nada, y para depurar "¿qué día cree que es?"."""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from asistente.application.agent.instrucciones import instrucciones
from asistente.application.prompts.sistema import SISTEMA
from asistente.domain.services.tokens import estimar_tokens
from asistente.infrastructure import container
from core.application.ports.i_reloj import IReloj
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Enseña el system prompt del asistente para un usuario, un hogar y (si quieres) otro momento."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--hogar", type=int, required=True)
        parser.add_argument("--ahora", type=datetime.fromisoformat, help="Otro momento, ISO 8601 (con zona)")

    def handle(self, *args, **o):
        usuario = Usuario.objects.filter(email__iexact=o["email"]).first()
        if usuario is None:
            raise CommandError(f"No hay ningún usuario con el email {o['email']}.")
        reloj = _RelojFijo(o["ahora"]) if o["ahora"] else None
        try:
            contexto = container.contexto(usuario.pk, o["hogar"], reloj=reloj)
        except SinPermisoException as e:
            raise CommandError(str(e)) from e
        texto = instrucciones(contexto)
        self.stdout.write(texto)
        self.stdout.write(
            self.style.HTTP_INFO(
                f"  [{SISTEMA.nombre} {SISTEMA.version} · huella {SISTEMA.huella} · {len(texto)} caracteres · "
                f"~{estimar_tokens(texto)} tokens estimados]"
            )
        )


class _RelojFijo(IReloj):
    def __init__(self, ahora: datetime):
        if ahora.tzinfo is None:
            raise CommandError("--ahora necesita zona horaria: 2027-01-15T12:00+00:00")
        self._ahora = ahora

    def ahora(self) -> datetime:
        return self._ahora

    def hoy(self):
        return self._ahora.date()
