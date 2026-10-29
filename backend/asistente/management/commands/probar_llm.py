# asistente/management/commands/probar_llm.py — una llamada al LLM a través del port, para verla con tus ojos (módulo 93)
"""manage.py probar_llm "pregunta" — una llamada al LLM configurado, con sus tokens, su latencia y su coste.

Antes de construir nada encima: la temperature, el razonamiento y el structured output, de verdad. No usa la base de
datos ni tools.

    uv run python manage.py probar_llm "Explica qué es un presupuesto doméstico en una frase"
    uv run python manage.py probar_llm "Inventa un nombre para una app de gastos" --veces 3 --temperatura 1.5
    uv run python manage.py probar_llm "ayer 23,40 en el Mercadona con la tarjeta" --estructurado
"""

import json
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from django.core.management.base import BaseCommand, CommandError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, WithJsonSchema, field_validator

from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.infrastructure import container
from asistente.infrastructure.llm.openai_compatible_llm import a_json
from core.infrastructure.clock.reloj_django import RelojDjango


# Ejercicio 1: UNA definición para las dos cosas. Su JSON Schema es lo que se pide al modelo (structured output) y su
# validación, lo que se le exige a la respuesta: el schema garantiza la forma; las reglas, el sentido. (Sin docstring:
# pydantic lo pondría en el schema como "description", y el modelo lo leería en cada llamada.)
class MovimientoExtraido(BaseModel):
    model_config = ConfigDict(extra="forbid")  # additionalProperties: false, lo que exige el modo estricto

    concepto: str = Field(min_length=1, max_length=255, description="Comercio o descripción corta")
    # Decimal (dinero), pero en el schema un number: es lo que escribe el modelo
    importe: Annotated[Decimal, WithJsonSchema({"type": "number"})] = Field(
        description="Negativo si es un gasto; positivo si es un ingreso"
    )
    fecha: date | None = Field(description="AAAA-MM-DD, o null si no se sabe")
    cuenta: Literal["Cuenta común", "Tarjeta", "Efectivo"] | None = Field(description="null si no se dice")

    @field_validator("importe")
    @classmethod
    def no_cero(cls, valor: Decimal) -> Decimal:
        valor = valor.quantize(Decimal("0.01"))  # el modelo puede escribir -23.399999
        if valor == 0:
            raise ValueError("un movimiento no puede ser de 0 €")
        return valor

    @field_validator("fecha")
    @classmethod
    def no_futura(cls, valor: date | None) -> date | None:
        if valor and valor > RelojDjango().hoy():
            raise ValueError("la fecha está en el futuro")
        return valor


# Structured output: el modelo DEBE devolver un JSON con esta forma (no "por favor, contesta en JSON"). En modo
# estricto, todos los campos van en required y los objetos con additionalProperties: false; pydantic ya lo escribe así
# (sin valores por defecto, todos son obligatorios; los opcionales son "X o null").
MOVIMIENTO = EsquemaRespuesta(nombre="movimiento", esquema=MovimientoExtraido.model_json_schema())


class Command(BaseCommand):
    help = "Hace una llamada al LLM configurado y muestra la respuesta, los tokens, la latencia y el coste."

    def add_arguments(self, parser):
        parser.add_argument("pregunta")
        parser.add_argument("--sistema", default="Responde en español, breve.")
        parser.add_argument("--modelo", help="Otro modelo en vez de ASISTENTE_MODELO")
        parser.add_argument("--temperatura", type=float)
        parser.add_argument("--esfuerzo", choices=[e.value for e in EsfuerzoDeRazonamiento])
        parser.add_argument("--max-tokens", type=int)
        parser.add_argument("--estructurado", action="store_true", help="Extraer un movimiento como JSON")
        parser.add_argument("--veces", type=int, default=1, help="Repetir la MISMA petición")
        parser.add_argument("--ver-razonamiento", action="store_true", help="Enseñar el razonamiento del modelo")
        parser.add_argument("--ver-peticion", action="store_true", help="Enseñar el JSON que se envía")

    def handle(self, *args, **o):
        llm = container.llm(o["modelo"])
        sistema = o["sistema"]
        if o["estructurado"]:  # sin la fecha de hoy, "ayer" no significa nada: el modelo no tiene reloj
            sistema = f"Extrae el movimiento bancario que describe el usuario. Hoy es {RelojDjango().hoy()}."
        peticion = PeticionLLM(
            sistema=sistema,
            mensajes=(Mensaje.usuario(o["pregunta"]),),
            esquema=MOVIMIENTO if o["estructurado"] else None,
            temperatura=o["temperatura"],
            esfuerzo=EsfuerzoDeRazonamiento(o["esfuerzo"]) if o["esfuerzo"] else None,
            max_tokens=o["max_tokens"],
        )
        if o["ver_peticion"]:
            self.stdout.write(a_json(peticion, llm.modelo))
        for _ in range(o["veces"]):
            try:
                r = llm.generar(peticion)
            except LLMException as e:
                raise CommandError(f"El LLM no responde: {e}") from e
            if o["ver_razonamiento"] and r.razonamiento:
                self.stdout.write(self.style.WARNING(f"(razonamiento) {r.razonamiento.strip()}"))
            texto = r.texto.strip()
            if o["estructurado"]:
                texto = _json(r)
            self.stdout.write(texto)
            self.stdout.write(self.style.HTTP_INFO(_resumen(r)))


def _json(r: RespuestaLLM) -> str:
    """Ejercicio 1: la salida de un LLM es una entrada externa y se valida, como el body de una request."""
    try:
        movimiento = MovimientoExtraido.model_validate_json(r.texto)
    except ValidationError as e:  # también un JSON roto: p. ej. cortado por max_tokens (motivo=limite_tokens)
        errores = "; ".join(f"{'.'.join(map(str, x['loc'])) or 'json'}: {x['msg']}" for x in e.errors())
        raise CommandError(f"El modelo no ha devuelto un movimiento válido ({r.motivo}): {errores}") from e
    return json.dumps(movimiento.model_dump(mode="json"), ensure_ascii=False)


def _resumen(r: RespuestaLLM) -> str:
    p = container.precio(r.modelo)
    coste = f"{p.coste(r.uso)} $" if p else "coste desconocido"
    u = r.uso
    return (
        f"  [{r.modelo} · {r.duracion_ms} ms · {r.motivo} · tokens: entrada {u.entrada}"
        f"{f' ({u.cache} de caché)' if u.cache else ''}, salida {u.salida} (razonamiento {u.razonamiento}) · {coste}]"
    )
