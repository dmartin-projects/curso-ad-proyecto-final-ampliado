# asistente/domain/services/fechas_en_castellano.py — fechas con palabras, sin depender del locale (módulo 96)
"""El modelo calcula mal los días de la semana y los años de "septiembre": se los damos calculados. Sin `locale`:
el del servidor (un contenedor suele tener C o en_US) no puede cambiar el prompt."""

from datetime import date

from core.domain.vo.mes import Mes

DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")  # fmt: skip


def fecha_larga(fecha: date) -> str:
    """'jueves, 29 de octubre de 2026'"""
    return f"{DIAS[fecha.weekday()]}, {fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def mes_largo(mes: Mes) -> str:
    """'octubre de 2026 (2026-10)': como lo dice el usuario y como lo piden las tools."""
    return f"{MESES[mes.numero - 1]} de {mes.anio} ({mes})"
