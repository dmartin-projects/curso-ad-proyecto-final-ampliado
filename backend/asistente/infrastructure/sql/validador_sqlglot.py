# asistente/infrastructure/sql/validador_sqlglot.py — el SQL del modelo, leído como un árbol (101, ejercicio 1)
"""validar_sql (dominio) mira el texto con expresiones regulares: sirve para los errores obvios, pero el SQL tiene
demasiadas formas de decir lo mismo. sqlglot lo convierte en un árbol (AST) y aquí se recorre: qué tablas lee, qué
funciones llama y qué tipo de sentencia es. Es una lista BLANCA (lo que se permite), no negra.

No sustituye a la base de datos (el rol, la RLS, el timeout): si sqlglot no entiende algo que PostgreSQL sí, la
consulta se rechaza aquí; si algo se le escapara, PostgreSQL lo para igual. Dos capas que fallan de forma distinta."""

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from asistente.domain.exceptions.consulta_sql_exception import ConsultaSQLException

VISTAS = frozenset({"movimientos", "categorias", "cuentas", "presupuestos"})
# Las funciones que sqlglot no conoce (llegan como Anonymous) y se permiten. Las que conoce (sum, count, date_trunc,
# extract, coalesce, round…) ya son de lectura. Fuera quedan pg_sleep, set_config, pg_read_file, dblink, lo_import…
FUNCIONES = frozenset({"to_char", "date_part", "unaccent", "initcap", "array_to_string", "string_agg", "nullif"})
PROHIBIDO = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command, exp.Merge, exp.Into)


def validar_arbol(sql: str) -> None:
    try:
        sentencias = sqlglot.parse(sql, read="postgres")
    except ParseError as e:
        raise ConsultaSQLException(f"No se entiende la consulta: {str(e).splitlines()[0][:200]}") from e
    if len(sentencias) != 1 or sentencias[0] is None:
        raise ConsultaSQLException("Una sola consulta.")
    arbol = sentencias[0]
    if not isinstance(arbol, exp.Query):
        raise ConsultaSQLException("Solo consultas de lectura (SELECT).")
    if prohibido := next(arbol.find_all(*PROHIBIDO), None):
        raise ConsultaSQLException(f"No se puede usar {prohibido.key.upper()} en una consulta de lectura.")
    ctes = {c.alias_or_name.lower() for c in arbol.find_all(exp.CTE)}
    for tabla in arbol.find_all(exp.Table):
        nombre = tabla.name.lower()
        if nombre in ctes and not tabla.db:
            continue
        if nombre not in VISTAS or tabla.db.lower() not in ("", "asistente_sql"):
            raise ConsultaSQLException(f"Solo las vistas {', '.join(sorted(VISTAS))}: «{tabla.sql()}» no.")
    for funcion in arbol.find_all(exp.Anonymous):
        if funcion.name.lower() not in FUNCIONES:
            raise ConsultaSQLException(f"La función {funcion.name} no está permitida.")
