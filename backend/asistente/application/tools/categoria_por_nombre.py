# asistente/application/tools/categoria_por_nombre.py — el argumento "categoria": un nombre, no un id (módulo 95)
import unicodedata

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.read_models.categoria_del_hogar import CategoriaDelHogar

# El modelo escribe lo que dice el usuario ("la luz", "supermercado"): un nombre. Un id le obligaría a llamar antes a
# listar_categorias (una vuelta más) y es un número de NUESTRA base de datos que no tiene por qué ver.
NOMBRE_DE_CATEGORIA = Field(
    max_length=60,
    description="El nombre como lo dice el usuario ('luz', 'súper'): si no existe, el error dice cuáles hay.",
)


def clave(texto: str) -> str:
    """Sin mayúsculas, tildes ni espacios de más: "nomina " es "Nómina"."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold().strip()


def categoria_por_nombre(finanzas: IConsultasDeFinanzas, contexto: ContextoPregunta, nombre: str) -> CategoriaDelHogar:
    """La categoría de ESTE hogar con ese nombre, o un error con las que hay: el modelo elige bien a la segunda."""
    categorias = finanzas.categorias(contexto.actor, contexto.hogar.id)
    for c in categorias:
        if clave(c.nombre) == clave(nombre):
            return c
    nombres = ", ".join(c.nombre for c in categorias)
    raise ToolException(f"No hay ninguna categoría «{nombre}» en este hogar. Las que hay: {nombres}.")
