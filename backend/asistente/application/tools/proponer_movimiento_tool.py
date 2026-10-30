# asistente/application/tools/proponer_movimiento_tool.py — apuntar un gasto, con confirmación (módulo 97)
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Annotated, Literal

from pydantic import AfterValidator, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.categoria_por_nombre import categoria_por_nombre, clave
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.periodo import FechaOpcional
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.read_models.cuenta_del_hogar import CuentaDelHogar
from asistente.domain.vo.propuesta_preparada import PropuestaPreparada

MAXIMO = Decimal("100000")


def _importe(texto: str) -> str:
    try:
        valor = Decimal(texto.replace(",", "."))
    except InvalidOperation:
        raise ValueError(f"«{texto}» no es un importe: usa un número con punto decimal, por ejemplo 12.50") from None
    if not 0 < valor < MAXIMO or valor != valor.quantize(Decimal("0.01")):
        raise ValueError(f"«{texto}»: el importe va en positivo, con dos decimales como mucho y menor de {MAXIMO}")
    return f"{valor:.2f}"


class ProponerMovimientoArgumentos(SinArgumentos):
    importe: Annotated[str, AfterValidator(_importe)] = Field(description="En positivo y con punto: '12.50'.")
    concepto: str = Field(min_length=1, max_length=120, description="Como lo diría el usuario: 'Churros en la feria'.")
    tipo: Literal["gasto", "ingreso"] = Field("gasto", description="Por defecto, un gasto.")
    fecha: FechaOpcional = Field(None, description="AAAA-MM-DD. Si no la dice el usuario: hoy.")
    categoria: str | None = Field(None, max_length=60, description="Una categoría del hogar, si el usuario la dice.")
    cuenta: str | None = Field(
        None, max_length=60, description="El nombre de la cuenta. Sin ella: la única activa, si solo hay una."
    )


def _euros(importe: str) -> str:
    return importe.replace(".", ",") + " €"


class ProponerMovimientoTool(Tool):
    nombre = "proponer_movimiento"
    descripcion = (
        "Prepara un gasto o un ingreso para apuntarlo. NO lo apunta: la persona lo confirma con un botón en el chat. "
        "Úsala solo si te piden apuntar algo, y di que queda pendiente de su confirmación."
    )
    Argumentos = ProponerMovimientoArgumentos
    max_llamadas = 3

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: ProponerMovimientoArgumentos) -> ConArtefacto:
        fecha = date.fromisoformat(args.fecha) if args.fecha else contexto.hoy
        if fecha > contexto.hoy:
            raise ToolException(
                f"La fecha {fecha} es futura (hoy es {contexto.hoy}): solo se apunta lo que ya ha pasado."
            )
        cuenta = self._cuenta(contexto, args.cuenta)
        categoria = categoria_por_nombre(self.finanzas, contexto, args.categoria) if args.categoria else None
        gasto = args.tipo == "gasto"
        resumen = (
            f"{'Gasto' if gasto else 'Ingreso'} de {_euros(args.importe)}: «{args.concepto}»"
            f"{f', en {categoria.nombre}' if categoria else ''}, el {fecha:%d/%m/%Y}, en {cuenta.nombre}"
        )
        datos = {  # lo que pedirá RegistrarMovimientoUseCase al confirmarla: ids ya comprobados contra el hogar
            "cuenta_id": cuenta.id,
            "fecha": fecha.isoformat(),
            "importe": f"-{args.importe}" if gasto else args.importe,  # en finanzas, un gasto es negativo
            "concepto": args.concepto,
            "categoria_id": categoria.id if categoria else None,
        }
        return ConArtefacto(
            {
                "propuesta": "preparada",
                "resumen": resumen,
                "nota": "Aún NO está apuntado: la persona tiene que confirmarlo en el chat. Díselo así.",
            },
            PropuestaPreparada(TipoPropuesta.MOVIMIENTO, resumen, datos),
        )

    def _cuenta(self, contexto: ContextoPregunta, nombre: str | None) -> CuentaDelHogar:
        cuentas = [c for c in self.finanzas.cuentas(contexto.actor, contexto.hogar.id) if c.activa]
        if nombre:
            for c in cuentas:
                if clave(c.nombre) == clave(nombre):
                    return c
            raise ToolException(
                f"No hay ninguna cuenta activa «{nombre}». Las que hay: {', '.join(c.nombre for c in cuentas)}."
            )
        if len(cuentas) == 1:
            return cuentas[0]
        raise ToolException(f"¿En qué cuenta? Pregúntaselo al usuario: {', '.join(c.nombre for c in cuentas)}.")
