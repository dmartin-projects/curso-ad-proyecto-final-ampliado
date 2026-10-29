# asistente/application/tools/tipo_de_cambio_tool.py — un importe en otra moneda, con el tipo del BCE (módulo 95)
from datetime import date
from decimal import Decimal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_tipo_de_cambio import ITipoDeCambio
from asistente.application.tools.periodo import FechaOpcional
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.exceptions.tool_exception import ToolException


class TipoDeCambioArgumentos(SinArgumentos):
    importe: Decimal = Field(gt=0, le=1_000_000, description="El importe a convertir, en positivo.")
    de: str = Field(min_length=3, max_length=3, description="Moneda de origen, ISO 4217: GBP, USD…")
    a: str | None = Field(None, min_length=3, max_length=3, description="Moneda de destino. Sin ella: la del hogar.")
    # El formato y la validación de FechaOpcional; la descripción dice CUÁNDO mandarla, no solo cómo
    fecha: FechaOpcional = Field(
        None, description="AAAA-MM-DD. El día del pago, si el usuario lo dice: el tipo cambia cada día. Sin ella: hoy."
    )


class TipoDeCambioTool(Tool):
    nombre = "tipo_de_cambio"
    descripcion = (
        "Convierte un importe a otra moneda con el tipo de referencia del Banco Central Europeo. Para viajes o compras "
        "en otra moneda: si el usuario dice cuándo pagó, manda esa fecha."
    )
    Argumentos = TipoDeCambioArgumentos

    def __init__(self, *, divisas: ITipoDeCambio):
        self.divisas = divisas

    def ejecutar(self, contexto: ContextoPregunta, args: TipoDeCambioArgumentos) -> dict:
        fecha = date.fromisoformat(args.fecha) if args.fecha else None
        if fecha and fecha > contexto.hoy:
            raise ToolException(f"La fecha {fecha} es futura: no hay tipo de cambio. Usa una hasta {contexto.hoy}.")
        destino = (args.a or contexto.hogar.moneda).upper()
        try:
            c = self.divisas.convertir(args.importe, args.de.upper(), destino, fecha)
        except ServicioExternoNoDisponibleException as e:
            raise ToolException(
                "El servicio de tipos de cambio del BCE no responde ahora. No des un tipo aproximado ni de memoria: "
                "dile al usuario que no puedes convertirlo en este momento."
            ) from e
        return {
            "importe": f"{c.importe:.2f} {c.de}",
            "resultado": f"{c.resultado:.2f} {c.a}",
            "tipo": f"1 {c.de} = {c.tipo} {c.a}",
            "fecha_del_tipo": str(c.fecha_del_tipo),
            **({"nota": "El BCE no publica en fines de semana ni festivos: es el del día hábil anterior."}
               if fecha and c.fecha_del_tipo != fecha else {}),
        }  # fmt: skip
