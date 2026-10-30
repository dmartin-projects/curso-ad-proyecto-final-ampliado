# asistente/management/commands/ver_contexto.py — lo que viajaría en una conversación (módulo 99, ejercicio 2)
"""manage.py ver_contexto --email … --hogar … --conversacion … — detrás del system prompt (manage.py ver_prompt) y de
las tools: los recuerdos, el resumen y la parte del historial que cabe. Sin llamar al modelo."""

from django.core.management.base import BaseCommand, CommandError

from asistente.application.ver_contexto_use_case.dtos.ver_contexto_input_dto import VerContextoInputDTO
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.infrastructure import container
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Enseña lo que viajaría al modelo en una conversación: memoria (recuerdos y resumen) e historial."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--hogar", type=int, required=True)
        parser.add_argument("--conversacion", type=int, required=True)

    def handle(self, *args, **o):
        usuario = Usuario.objects.filter(email__iexact=o["email"]).first()
        if usuario is None:
            raise CommandError(f"No hay ningún usuario con el email {o['email']}.")
        entrada = VerContextoInputDTO(o["hogar"], Actor(usuario.pk, Rol.LECTOR), o["conversacion"])
        try:
            partes = container.ver_contexto().ejecutar(entrada)
        except ConversacionNoEncontradaException as e:
            raise CommandError("Esa conversación no es de ese usuario en ese hogar.") from e
        for p in partes:
            self.stdout.write(self.style.HTTP_INFO(f"── {p.rol} (~{p.tokens} tokens)"))
            self.stdout.write(p.texto)
        total = sum(p.tokens for p in partes)
        self.stdout.write(self.style.HTTP_INFO(f"  [{len(partes)} mensajes · ~{total} tokens estimados]"))
