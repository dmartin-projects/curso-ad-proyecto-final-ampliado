# asistente/application/tools/sin_argumentos.py — la base de los argumentos de una tool (módulo 94)
from pydantic import BaseModel, ConfigDict


class SinArgumentos(BaseModel):
    """Lo que hereda cada modelo de argumentos. extra="forbid": un argumento que la tool no tiene (un hogar_id que
    el modelo se inventa) es un error que el modelo lee, no algo que se ignora en silencio."""

    model_config = ConfigDict(extra="forbid")
