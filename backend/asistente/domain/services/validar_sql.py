# asistente/domain/services/validar_sql.py — lo que se comprueba ANTES de mandar una consulta (módulo 101)
"""Defensa en profundidad: la que de verdad protege es la base de datos (un rol que solo lee, Row Level Security,
statement_timeout). Esto da al modelo un error claro y pronto, y descarta lo obviamente fuera de lugar; no es una
lista negra que pretenda cubrir todo el SQL (no se puede: siempre hay otra forma de escribirlo)."""

import re

from asistente.domain.exceptions.consulta_sql_exception import ConsultaSQLException

MAX_CARACTERES = 3000


def validar_sql(sql: str) -> str:
    """El SQL limpio (sin el ";" final), o ConsultaSQLException con lo que el modelo tiene que corregir."""
    limpio = sql.strip().rstrip(";").strip()
    if not limpio:
        raise ConsultaSQLException("La consulta está vacía.")
    if len(limpio) > MAX_CARACTERES:
        raise ConsultaSQLException(f"La consulta es demasiado larga (más de {MAX_CARACTERES} caracteres).")
    sin_cadenas = re.sub(r"'(?:[^']|'')*'", "''", limpio)  # el ";" de un texto entre comillas no separa nada
    if ";" in sin_cadenas:
        raise ConsultaSQLException("Una sola consulta: sin «;» en medio.")
    if "--" in sin_cadenas or "/*" in sin_cadenas:
        raise ConsultaSQLException("Sin comentarios en la consulta.")
    if not re.match(r"(?is)^(select|with)\b", limpio):
        raise ConsultaSQLException("Solo consultas de lectura: tiene que empezar por SELECT o WITH.")
    return limpio
