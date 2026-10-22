# tickets/infrastructure/ia/cliente_ia.py — el cliente de la IA: convierte el texto (y si hace falta la imagen) de
# un ticket en datos estructurados (módulos 74, 84 y 88)
#
# Habla el formato *Chat Completions* de OpenAI, que hoy entienden casi todos los proveedores
# (Gemini, OpenAI, Mistral, Groq…) y también Ollama en local. Cambiar de proveedor = cambiar
# IA_BASE_URL, IA_MODELO e IA_API_KEY. El resto del proyecto solo conoce la interfaz IExtractorDeDatos; su
# adapter (extractor_ia.py) usa este cliente y el circuit breaker, y devuelve un DatosTicket del dominio.

import base64
import functools
import json
import time

import httpx
from django.conf import settings
from opentelemetry import metrics, trace

from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from tickets.infrastructure.ia.datos_ticket_serializer import validar
from tickets.infrastructure.ia.respuesta_ia_exception import RespuestaIAException
from tickets.infrastructure.ia.transitorio_ia_exception import TransitorioIAException

breaker_ia = CircuitBreaker("ia", umbral=5, enfriamiento=120)

# Módulo 84, ejercicio 3: cuánto tarda la IA, por modelo. Cubos pensados para un LLM (de 10 ms a 30 s): con
# los cubos por defecto el p95 no diría nada (lo mismo que con la duración de las tareas, §2).
# En Prometheus: gastos_ia_duracion_seconds_bucket{gen_ai_request_model="…"}
duracion_ia = metrics.get_meter("gastos.tickets").create_histogram(
    "gastos.ia.duracion",
    unit="s",
    description="Duración de las llamadas a la IA, por modelo",
    explicit_bucket_boundaries_advisory=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 20, 30],
)

INSTRUCCIONES = """Extraes datos de tickets de compra (normalmente españoles) a partir del texto de un OCR,
que puede tener errores de lectura. Reglas:
- comercio: nombre comercial corto, sin forma jurídica ni dirección ("Mercadona", no "MERCADONA S.A. C/ Mayor 3").
- fecha: AAAA-MM-DD; las fechas españolas vienen como DD/MM/AAAA. Cadena vacía si no aparece.
- total: el importe TOTAL pagado, positivo, con punto decimal. null si no lo encuentras.
- lineas: los productos con cantidad y precio unitario; no incluyas subtotales, IVA ni el total.
- categoria: una de las categorías permitidas, o cadena vacía si ninguna encaja.
- confianza: de 0 a 1, cuánto te fías de comercio, fecha y total. Baja si el texto está muy dañado.
No inventes datos: si algo no aparece, déjalo vacío."""


def esquema(categorias: list[str]) -> dict:
    """JSON Schema de la respuesta. Las categorías del hogar van como enum: la IA no puede inventarlas."""
    linea = {
        "type": "object",
        "properties": {
            "descripcion": {"type": "string"},
            "cantidad": {"type": "number"},
            "precio_unitario": {"type": "number"},
        },
        "required": ["descripcion", "cantidad", "precio_unitario"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "comercio": {"type": "string"},
            "nif": {"type": "string"},
            "fecha": {"type": "string"},
            "total": {"type": ["number", "null"]},
            "moneda": {"type": "string"},
            "categoria": {"type": "string", "enum": [*categorias, ""]},
            "lineas": {"type": "array", "items": linea},
            "confianza": {"type": "number"},
        },
        "required": ["comercio", "nif", "fecha", "total", "moneda", "categoria", "lineas", "confianza"],
        "additionalProperties": False,
    }


class ClienteIA:
    def __init__(self, *, base_url: str, api_key: str, modelo: str, timeout: float = 30.0, compartido=False):
        self.modelo = modelo
        self._compartido = compartido
        self._http = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(timeout, connect=5.0),
        )

    @classmethod
    def desde_settings(cls) -> "ClienteIA":
        """El cliente del proceso: se crea una vez y lo reutilizan todos los tickets.

        Crear un httpx.Client no es gratis (carga los certificados y prepara el contexto TLS: decenas de ms),
        y reutilizarlo mantiene la conexión abierta (keep-alive): con la IA real, por HTTPS, cada llamada se
        ahorra además el saludo TLS. Se crea en el primer uso, ya dentro del proceso hijo de Celery: una
        conexión abierta antes del fork quedaría compartida entre procesos.
        """
        return _cliente_del_proceso(settings.IA_BASE_URL, settings.IA_API_KEY, settings.IA_MODELO, settings.IA_TIMEOUT)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if not self._compartido:  # el del proceso vive mientras viva el proceso
            self._http.close()

    def extraer_ticket(self, texto: str, categorias: list[str], imagen_png: bytes | None = None) -> dict:
        contenido: list[dict] = [
            {"type": "text", "text": f"Categorías permitidas: {', '.join(categorias)}\n\nTexto del ticket:\n{texto}"}
        ]
        if imagen_png:  # el OCR no ha leído nada útil: que la IA mire la imagen (modelos multimodales)
            datos_url = "data:image/png;base64," + base64.b64encode(imagen_png).decode()
            contenido.append({"type": "image_url", "image_url": {"url": datos_url}})
        cuerpo = {
            "model": self.modelo,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": INSTRUCCIONES},
                {"role": "user", "content": contenido},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "ticket", "strict": True, "schema": esquema(categorias)},
            },
        }
        return validar(self._enviar(cuerpo))

    def _enviar(self, cuerpo: dict) -> dict:
        modelo = {"gen_ai.request.model": self.modelo}
        inicio = time.perf_counter()
        try:
            r = self._http.post("chat/completions", json=cuerpo)
        except httpx.TransportError as e:  # timeouts, conexión rechazada, DNS…
            duracion_ia.record(time.perf_counter() - inicio, modelo | {"error.type": e.__class__.__name__})
            raise TransitorioIAException(f"Error de red: {e.__class__.__name__}") from e
        duracion_ia.record(time.perf_counter() - inicio, modelo)
        self._anotar_span(r)
        if r.status_code == 429 or r.status_code >= 500:
            raise TransitorioIAException(f"HTTP {r.status_code}")
        if r.is_error:  # 400/401/403/404: petición o configuración incorrectas
            raise RespuestaIAException(f"HTTP {r.status_code}: {r.text[:300]}")
        try:
            return json.loads(r.json()["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise RespuestaIAException("La respuesta no contiene un JSON válido") from e

    def _anotar_span(self, r: httpx.Response) -> None:
        """Atributos GenAI (semantic conventions de OpenTelemetry) en el span en curso: ticket.ia.

        El modelo y los tokens (lo que se paga) sí; el prompt y la respuesta, nunca: son el texto del ticket.
        """
        span = trace.get_current_span()
        if not span.is_recording():
            return
        span.set_attributes({"gen_ai.operation.name": "chat", "gen_ai.request.model": self.modelo})
        try:
            respuesta = r.json()
        except ValueError:
            return
        if not isinstance(respuesta, dict):
            return
        if modelo := respuesta.get("model"):  # el que ha contestado de verdad (p. ej. con fecha de versión)
            span.set_attribute("gen_ai.response.model", modelo)
        uso = respuesta.get("usage") or {}  # Chat Completions: prompt_tokens / completion_tokens
        for origen, destino in (("prompt_tokens", "input_tokens"), ("completion_tokens", "output_tokens")):
            if isinstance(uso.get(origen), int):
                span.set_attribute(f"gen_ai.usage.{destino}", uso[origen])


@functools.lru_cache(maxsize=4)  # uno por configuración (en los tests, settings cambia entre pruebas)
def _cliente_del_proceso(base_url: str, api_key: str, modelo: str, timeout: float) -> ClienteIA:
    return ClienteIA(base_url=base_url, api_key=api_key, modelo=modelo, timeout=timeout, compartido=True)
