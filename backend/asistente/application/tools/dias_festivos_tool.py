# asistente/application/tools/dias_festivos_tool.py — los festivos de un año, nacionales y de una comunidad (módulo 95, ejercicio 1)
import re
from typing import Annotated

from pydantic import AfterValidator, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_festivos import IFestivos
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.exceptions.tool_exception import ToolException

DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
# Lo que la fuente NO tiene, dicho en el resultado: sin esto, el modelo presenta la lista como completa
SIN_LOCALES = "Nacionales y autonómicos. No incluye los locales de cada municipio (dos al año): si preguntan, dilo."


def _comunidad(texto: str | None) -> str | None:
    if texto is not None and not re.fullmatch(r"ES-[A-Z]{2}", texto.upper()):
        raise ValueError(f"«{texto}» no es un código de comunidad: usa ES-MD, ES-CT, ES-AN…")
    return texto.upper() if texto else None


class DiasFestivosArgumentos(SinArgumentos):
    anio: int | None = Field(None, description="El año. Sin él: el año en curso del hogar.")
    comunidad: Annotated[
        str | None,
        AfterValidator(_comunidad),
        Field(description="Código ISO 3166-2 de la comunidad: ES-MD (Madrid), ES-CT (Cataluña)… Sin ella: nacionales."),
    ] = None
    desde_hoy: bool = Field(False, description='true: solo los que quedan desde hoy ("¿qué festivos nos quedan?").')


class DiasFestivosTool(Tool):
    nombre = "dias_festivos"
    descripcion = (
        "Los festivos oficiales de un año en España: los nacionales y, con 'comunidad', los de esa comunidad. Para "
        "explicar gastos de puentes y vacaciones o planear los próximos."
    )
    Argumentos = DiasFestivosArgumentos
    max_llamadas = 2

    def __init__(self, *, festivos: IFestivos):
        self.festivos = festivos

    def ejecutar(self, contexto: ContextoPregunta, args: DiasFestivosArgumentos) -> dict:
        hoy = contexto.hoy
        anio = args.anio or hoy.year
        if not hoy.year - 5 <= anio <= hoy.year + 1:
            raise ToolException(f"Solo hay festivos de {hoy.year - 5} a {hoy.year + 1}.")
        try:
            todos = self.festivos.del_anio(anio, "ES")
        except ServicioExternoNoDisponibleException as e:
            raise ToolException(
                "El calendario de festivos no responde ahora. No los des de memoria: dile al usuario que no puedes "
                "consultarlo en este momento."
            ) from e
        return {
            "anio": anio,
            "hoy": str(hoy),
            "festivos": [
                {
                    "fecha": str(f.fecha),
                    "dia": DIAS[f.fecha.weekday()],
                    "nombre": f.nombre,
                    "ambito": "nacional" if f.nacional else args.comunidad,
                }
                for f in todos
                if (f.nacional or args.comunidad in f.comunidades) and (not args.desde_hoy or f.fecha >= hoy)
            ],
            "nota": SIN_LOCALES,
        }
