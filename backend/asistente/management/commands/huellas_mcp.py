# asistente/management/commands/huellas_mcp.py — las tools de un servidor MCP, para aprobarlas (módulo 104)
"""manage.py huellas_mcp <nombre> — las tools que ofrece un servidor de ASISTENTE_MCP_SERVIDORES, con su huella y su
descripción, y si están aprobadas. Para aprobar una: leer su descripción ENTERA (es lo que leerá el modelo) y copiar
su huella en "aprobadas". Si el servidor cambia la tool, la huella cambia y queda fuera hasta que alguien la mire."""

from django.core.management.base import BaseCommand, CommandError

from asistente.infrastructure import container


class Command(BaseCommand):
    help = "Las tools de un servidor MCP configurado, con su huella, para aprobarlas."

    def add_arguments(self, parser):
        parser.add_argument("nombre")

    def handle(self, *args, nombre, **options):
        servidor = next((s for s in container.servidores_mcp() if s.nombre == nombre), None)
        if servidor is None:
            raise CommandError(f"No hay ningún servidor «{nombre}» en ASISTENTE_MCP_SERVIDORES.")
        for tool, h, descripcion in servidor.todas_con_huella():
            estado = {None: "sin aprobar", h: "aprobada"}.get(servidor.aprobadas.get(tool), "CAMBIADA")
            self.stdout.write(f"{tool:<28} {h}  {estado}\n    {descripcion}")
