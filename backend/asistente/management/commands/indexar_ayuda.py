# asistente/management/commands/indexar_ayuda.py — el índice de la ayuda, al día (módulo 100)
"""manage.py indexar_ayuda [--reconstruir] — después de cambiar un .md de asistente/ayuda/ (en el despliegue, tras
migrate). Incremental: solo recalcula lo que ha cambiado; --reconstruir, todo (al cambiar de modelo de embeddings)."""

from django.core.management.base import BaseCommand

from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.infrastructure import container


class Command(BaseCommand):
    help = "Pone al día el índice de la ayuda del asistente (pgvector y búsqueda de texto)."

    def add_arguments(self, parser):
        parser.add_argument("--reconstruir", action="store_true", help="Borrar el índice y calcularlo de cero")

    def handle(self, *args, **o):
        r = container.indexar_ayuda().ejecutar(IndexarAyudaInputDTO(reconstruir=o["reconstruir"]))
        modelo = f"con {r.modelo}" if r.modelo else "SIN vectores (sin modelo de embeddings): solo búsqueda por texto"
        self.stdout.write(
            f"{r.trozos} trozos: {r.nuevos_o_cambiados} nuevos o cambiados, {r.borrados} borrados; {modelo}."
        )
