# asistente/management/commands/preguntar.py — hablar con los datos de un hogar desde la terminal (módulos 94 y 96)
"""manage.py preguntar "pregunta" --email … --hogar … — el agente completo: el modelo, sus tools y tus datos.

Enseña cada paso: lo que pide el modelo, lo que devuelve cada tool, y al final las vueltas, los tokens y el coste.

    uv run python manage.py preguntar "¿Cuánto gastamos en septiembre?" --email demo@example.com --hogar 1
"""

import json
from dataclasses import asdict
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.vo.mensaje import Mensaje
from asistente.infrastructure import container
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Pregunta al asistente por los datos de un hogar y enseña cada paso del agente."

    def add_arguments(self, parser):
        parser.add_argument("pregunta")
        parser.add_argument("--email", required=True, help="Quién pregunta (sus permisos son los del agente)")
        parser.add_argument("--hogar", type=int, required=True, help="El id del hogar")
        parser.add_argument("--modelo", help="Un modelo concreto, sin reserva")
        parser.add_argument("--resultados", action="store_true", help="Enseñar lo que devuelve cada tool")
        parser.add_argument(
            "--estructurada", action="store_true", help="La respuesta también en JSON (una llamada más)"
        )

    def handle(self, *args, **o):
        usuario = Usuario.objects.filter(email__iexact=o["email"]).first()
        if usuario is None:
            raise CommandError(f"No hay ningún usuario con el email {o['email']}.")
        try:
            contexto = container.contexto(usuario.pk, o["hogar"])
        except SinPermisoException as e:
            raise CommandError(str(e)) from e
        pasos = Pasos(self, o["resultados"])
        agente = container.agente(pasos, modelo=o["modelo"])
        try:
            r = agente.responder((Mensaje.usuario(o["pregunta"]),), contexto, estructurada=o["estructurada"])
        except LLMException as e:
            raise CommandError(f"El asistente no está disponible: {e}") from e
        self.stdout.write(r.texto)
        if r.estructurada:
            self.stdout.write(json.dumps(asdict(r.estructurada), ensure_ascii=False, indent=2))
        u = r.uso
        self.stdout.write(
            self.style.HTTP_INFO(
                f"  [{r.motivo} · {r.iteraciones} vueltas · {len(r.llamadas)} tool calls · {r.duracion_ms} ms · "
                f"tokens: entrada {u.entrada}{f' ({u.cache} de caché)' if u.cache else ''}, salida {u.salida} "
                f"(razonamiento {u.razonamiento}) · {f'{pasos.coste} $' if pasos.coste is not None else 'coste desconocido'}]"
            )
        )


class Pasos(IObservadorAgente):
    """Cada paso del agente, en la terminal."""

    def __init__(self, comando: BaseCommand, resultados: bool):
        self.out, self.estilo, self.resultados = comando.stdout, comando.style, resultados
        self.vuelta = 0
        self.coste = Decimal(0)  # cada vuelta, con el precio del modelo que la contestó (con reserva, pueden ser dos)

    def respuesta(self, r):
        self.vuelta += 1
        precio = container.precio(r.modelo)
        self.coste = self.coste + precio.coste(r.uso) if precio and self.coste is not None else None
        self.out.write(
            self.estilo.HTTP_INFO(
                f"vuelta {self.vuelta} · {r.modelo} · {r.duracion_ms} ms · {r.motivo} · "
                f"entrada {r.uso.entrada}, salida {r.uso.salida}"
            )
        )

    def llamada(self, llamada):
        self.out.write(f"  → {llamada.nombre} {llamada.argumentos}")

    def resultado(self, resultado, duracion_ms):
        if resultado.es_error:
            self.out.write(self.estilo.WARNING(f"  ← {resultado.nombre} ({duracion_ms} ms): {resultado.contenido}"))
        elif self.resultados:
            self.out.write(f"  ← {resultado.nombre} ({duracion_ms} ms): {resultado.contenido}")
        else:
            self.out.write(f"  ← {resultado.nombre} ({duracion_ms} ms): {len(resultado.contenido)} caracteres")
