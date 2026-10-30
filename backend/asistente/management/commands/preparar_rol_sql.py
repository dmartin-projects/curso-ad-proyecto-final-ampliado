# asistente/management/commands/preparar_rol_sql.py — la contraseña del rol del text-to-SQL (módulo 101)
"""manage.py preparar_rol_sql — tras migrate, con ASISTENTE_SQL_PASSWORD en el entorno. El rol lo crea la migración
SIN login: una contraseña no va en una migración (quedaría en el repositorio y en cada base de datos). Rotarla es
cambiar la variable y volver a ejecutar esto."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from psycopg import sql


class Command(BaseCommand):
    help = "Da LOGIN y contraseña al rol de PostgreSQL del text-to-SQL del asistente."

    def add_arguments(self, parser):
        parser.add_argument("--si-hay", action="store_true", help="Sin contraseña, no hacer nada (en el despliegue)")

    def handle(self, *args, **o):
        if not settings.ASISTENTE_SQL_PASSWORD and o["si_hay"]:
            self.stdout.write("Sin ASISTENTE_SQL_PASSWORD: el text-to-SQL, apagado.")
            return
        if not settings.ASISTENTE_SQL_PASSWORD:
            raise CommandError("Sin ASISTENTE_SQL_PASSWORD: el rol se queda sin login (y consultar_sql, apagada).")
        with connections["default"].cursor() as c:
            c.execute(
                sql.SQL("ALTER ROLE {} LOGIN PASSWORD {} CONNECTION LIMIT 10").format(
                    sql.Identifier(settings.ASISTENTE_SQL_USUARIO), sql.Literal(settings.ASISTENTE_SQL_PASSWORD)
                )
            )
        self.stdout.write(f"Rol {settings.ASISTENTE_SQL_USUARIO}: con login (máximo 10 conexiones).")
