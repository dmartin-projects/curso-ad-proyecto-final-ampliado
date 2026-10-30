# asistente/infrastructure/sql/consultas_sql_postgres.py — el SQL del modelo, con el rol del asistente (módulo 101)
"""Cuatro barreras, de fuera adentro:

1. validar_sql (dominio): una sola consulta de lectura, sin comentarios (errores claros para el modelo);
2. la conexión es OTRA, la del rol `gastos_asistente_sql` (con psycopg, fuera del ORM: una conexión nueva por consulta
   y que ningún otro código de la app pueda usar por error): sin permisos de escritura y con SELECT solo en algunas
   columnas. Nunca un SET ROLE sobre la conexión de la app: `set_config('role', 'gastos', true)` en la consulta la
   devolvería a la app;
3. Row Level Security: el rol ve las filas del hogar escrito en `asistente_sql.contexto` para el pid de ESTA conexión,
   una tabla que el rol no puede ni leer ni escribir (la escribe aquí la conexión de la aplicación, antes, y la borra
   después);
4. la transacción: solo lectura, `statement_timeout` y un LIMIT por fuera (y nunca más filas de las que se leen).
"""

import time

import psycopg
from django.conf import settings
from django.db import connections

from asistente.application.ports.i_consultas_sql import IConsultasSQL
from asistente.domain.exceptions.consulta_sql_exception import ConsultaSQLException
from asistente.domain.read_models.resultado_sql import ResultadoSQL


class ConsultasSQLPostgres(IConsultasSQL):
    def disponible(self):
        return bool(settings.ASISTENTE_SQL_PASSWORD)

    def ejecutar(self, hogar_id, sql):
        limite = settings.ASISTENTE_SQL_FILAS
        inicio = time.perf_counter()
        try:
            with psycopg.connect(**_datos_de_conexion(), autocommit=False) as conexion, conexion.cursor() as c:
                c.execute("SET TRANSACTION READ ONLY")
                c.execute("SELECT set_config('statement_timeout', %s, true)", [f"{settings.ASISTENTE_SQL_SEGUNDOS}s"])
                c.execute("SELECT pg_backend_pid()")
                pid = c.fetchone()[0]
                _contexto(pid, hogar_id)
                try:
                    c.execute(f"SELECT * FROM ({sql}) AS consulta LIMIT {limite + 1}")  # noqa: S608 (es la idea)
                    columnas = tuple(d.name for d in c.description)
                    filas = c.fetchmany(limite + 1)
                finally:
                    _contexto(pid, None)
                    conexion.rollback()  # solo leía: nada que confirmar
        except psycopg.Error as e:
            raise ConsultaSQLException(_explicar(e)) from e
        return ResultadoSQL(
            columnas, tuple(filas[:limite]), len(filas) > limite, int((time.perf_counter() - inicio) * 1000)
        )


def _datos_de_conexion() -> dict:
    """La base de datos de la app (en los tests, la de pruebas: Django cambia el NAME), con el usuario del rol."""
    d = connections["default"].settings_dict
    return {
        "host": d["HOST"],
        "port": d["PORT"] or 5432,
        "dbname": d["NAME"],
        "user": settings.ASISTENTE_SQL_USUARIO,
        "password": settings.ASISTENTE_SQL_PASSWORD,
        "connect_timeout": 5,
        "application_name": "gastos-asistente-sql",
    }


def _contexto(pid: int, hogar_id: int | None) -> None:
    """Con la conexión de la APLICACIÓN, en su propia transacción: tiene que estar confirmado para que la otra conexión
    lo vea (y la consulta del modelo suele correr fuera de cualquier transacción de la app)."""
    with connections["default"].cursor() as c:
        if hogar_id is None:
            c.execute("DELETE FROM asistente_sql.contexto WHERE pid = %s", [pid])
        else:
            c.execute(
                "INSERT INTO asistente_sql.contexto (pid, hogar_id) VALUES (%s, %s) "
                "ON CONFLICT (pid) DO UPDATE SET hogar_id = EXCLUDED.hogar_id, desde = now()",
                [pid, hogar_id],
            )


def _explicar(e: psycopg.Error) -> str:
    """El mensaje de PostgreSQL es lo que el modelo necesita para corregirse ("column «total» does not exist"), sin la
    consulta entera (ya la tiene) y recortado."""
    mensaje = ((e.diag.message_primary if e.diag else None) or str(e)).strip()
    if isinstance(e, psycopg.errors.DataError):
        # SQLSTATE clase 22: un VALOR de las filas no encaja, y PostgreSQL lo cita ("invalid input syntax for type
        # integer: «el concepto»"). El valor no viaja: puede ser texto de un extracto, y el modelo lo leería como un
        # mensaje nuestro. Basta la clase del error para corregir la consulta
        return f"Error de PostgreSQL: {mensaje.split(':', 1)[0]} (un valor de las filas no encaja: filtra o convierte)."
    if isinstance(e, psycopg.errors.QueryCanceled):
        return f"La consulta tarda más de {settings.ASISTENTE_SQL_SEGUNDOS} s: simplifícala (agrupa, filtra fechas)."
    if isinstance(e, psycopg.errors.InsufficientPrivilege):
        return f"Sin permiso: {mensaje}. Solo puedes leer las vistas movimientos, categorias, cuentas y presupuestos."
    return f"Error de PostgreSQL: {mensaje}"[:300]
