# asistente/application/tools/consultar_sql_tool.py — text-to-SQL: el modelo escribe la consulta (módulo 101)
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_sql import IConsultasSQL
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.tool import Tool
from asistente.domain.services.validar_sql import validar_sql
from asistente.domain.vo.consulta_sql import ConsultaSQL

# Lo que el modelo sabe de la base de datos: SOLO estas vistas (el rol no ve nada más). Cada línea, una pista medida:
# el signo del importe, la categoría padre, que las fechas son DATE
ESQUEMA = (
    "PostgreSQL, solo lectura y solo los datos del hogar de quien pregunta. Vistas: "
    "movimientos(fecha date, importe numeric: <0 gasto y >0 ingreso, concepto, categoria, categoria_padre, cuenta, "
    "comercio, etiquetas text[]); categorias(nombre, padre, es_ingreso); cuentas(nombre, tipo, activa); "
    "presupuestos(mes date: día 1, categoria, importe). Usa date_trunc, sum, count, group by y order by; "
    "agrupa en la base de datos, no pidas filas sueltas para sumarlas tú."
)


class ConsultarSQLArgumentos(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sql: str = Field(min_length=6, max_length=3000, description=f"Un SELECT (o WITH). {ESQUEMA}")


class ConsultarSQLTool(Tool):
    """La alternativa a un catálogo de tools: una sola tool que acepta cualquier consulta. Cubre preguntas que ninguna
    tool prevé ("¿qué día de la semana gastamos más?"), a cambio de lo que el módulo 101 mide: más tokens, más vueltas
    cuando el SQL falla, y una superficie de ataque que solo se puede cerrar en la base de datos."""

    nombre = "consultar_sql"
    descripcion = (
        "Consulta los datos del hogar con SQL de solo lectura, para lo que ninguna otra tool contesta. Devuelve como "
        "mucho 50 filas: agrupa y suma en la consulta."
    )
    Argumentos = ConsultarSQLArgumentos
    lee_terceros = True  # módulo 102: las filas pueden llevar conceptos de extractos
    max_llamadas = 3

    def __init__(self, *, consultas: IConsultasSQL):
        self.consultas = consultas

    def ejecutar(self, contexto: ContextoPregunta, args: ConsultarSQLArgumentos) -> ConArtefacto:
        sql = validar_sql(args.sql)
        r = self.consultas.ejecutar(contexto.hogar.id, sql)
        filas = [[_json(v) for v in fila] for fila in r.filas]
        para_el_modelo = {"columnas": list(r.columnas), "filas": filas[:50], "total_filas": len(filas)}
        if r.recortado or len(filas) > 50:
            para_el_modelo["nota"] = "Hay más filas de las que ves: agrupa o filtra más si necesitas el total."
        return ConArtefacto(para_el_modelo, ConsultaSQL(sql, r.columnas, tuple(tuple(f) for f in filas), r.recortado))


def _json(valor):
    """Lo que PostgreSQL devuelve, en JSON: los importes como texto con dos decimales (como euros(), módulo 95)."""
    if isinstance(valor, Decimal):
        return f"{valor:.2f}"
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, list | tuple):
        return [_json(v) for v in valor]
    return valor
