# asistente/infrastructure/llm/openai_compatible_llm.py — el port ILLM sobre la API Chat Completions (módulos 93 y 97)
#
# Chat Completions es el formato de OpenAI, y lo hablan casi todos: Groq (el proveedor del curso), OpenRouter,
# Together, Cerebras, Mistral, Gemini (su capa de compatibilidad) y, en local, Ollama, vLLM o LM Studio. Por eso el
# adapter no se llama "GroqLLM": cambiar de proveedor es cambiar base_url, la clave y el modelo.
#
# Es el ÚNICO archivo del proyecto que importa el SDK `openai`. Traduce en los dos sentidos (PeticionLLM → el JSON de
# Chat Completions; la respuesta → RespuestaLLM) y convierte los errores del SDK en los del dominio.
import json
import logging
import time
from collections.abc import Callable

import httpx2
import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential_jitter

from asistente.application.ports.i_llm import ILLM
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.uso import Uso

logger = logging.getLogger(__name__)

# Se reintentan los errores del servidor y de la red. El 429 NO: puede ser la cuota por minuto (vuelve en 2 s) o la
# diaria (vuelve mañana), y lo dice la cabecera retry-after. Lo decide quien sabe qué hacer: otro modelo (módulo 94).
REINTENTABLES = {408, 409, 498, 500, 502, 503, 504}  # 498: la capa flex de Groq, sin capacidad
# Un 400 que no es culpa de la petición: el modelo ha escrito una tool call que no se puede interpretar (Groq lo
# devuelve con este código y el texto en failed_generation). El muestreo es aleatorio: repetir suele funcionar.
CODIGOS_REINTENTABLES = {"tool_use_failed"}
ESFUERZOS = {"bajo": "low", "medio": "medium", "alto": "high"}
MOTIVOS = {
    "stop": MotivoFin.FIN,
    "tool_calls": MotivoFin.TOOLS,
    "function_call": MotivoFin.TOOLS,
    "length": MotivoFin.LIMITE_TOKENS,
    "content_filter": MotivoFin.BLOQUEADA,
}


class OpenAICompatibleLLM(ILLM):
    def __init__(self, *, cliente: OpenAI, modelo: str, intentos: int = 2, pausa: float = 0.5):
        self._cliente = cliente  # uno por proceso (container.py): reutiliza la conexión HTTPS
        self._modelo = modelo
        self._intentos = intentos  # por petición, el primero incluido
        self._pausa = pausa  # la primera espera antes de reintentar (en los tests, 0)

    @property
    def modelo(self) -> str:
        return self._modelo

    def generar(self, peticion: PeticionLLM) -> RespuestaLLM:
        cuerpo = _cuerpo(self._modelo, peticion)
        inicio = time.perf_counter()
        try:
            for intento in Retrying(
                stop=stop_after_attempt(self._intentos),
                # 0,5 s, 1 s, 2 s… más un azar (jitter): mil clientes que fallan a la vez no reintentan a la vez
                wait=wait_exponential_jitter(multiplier=self._pausa, max=4, jitter=self._pausa),
                retry=retry_if_exception(_reintentable),
                before_sleep=lambda estado: logger.warning(
                    "LLM %s: %s; reintento", self._modelo, _describir(estado.outcome.exception())
                ),
                reraise=True,
            ):
                with intento:
                    completion = self._cliente.chat.completions.create(**cuerpo)
        except openai.RateLimitError as e:
            raise LLMNoDisponibleException(f"{self._modelo}: {_describir(e)}", _retry_after(e.response)) from e
        except openai.APIStatusError as e:
            if _reintentable(e):
                raise LLMNoDisponibleException(f"{self._modelo}: {_describir(e)}") from e
            raise PeticionLLMException(f"{self._modelo}: {_describir(e)}") from e
        except openai.APIConnectionError as e:  # también APITimeoutError: sin respuesta del servidor
            raise LLMNoDisponibleException(f"{self._modelo}: {_describir(e)}") from e
        return _respuesta(completion, self._modelo, int((time.perf_counter() - inicio) * 1000))

    def generar_en_streaming(self, peticion: PeticionLLM, al_texto: Callable[[str], None]) -> RespuestaLLM:
        """Módulo 97: stream=True. El servidor manda la respuesta en trozos (Server-Sent Events) y cada trozo de texto
        sale por `al_texto` en cuanto llega; las tool calls llegan también en trozos y se juntan aquí. Al final, la
        misma RespuestaLLM que sin streaming (con el uso: stream_options.include_usage lo pide en el último trozo).

        Se reintenta solo si aún no ha salido ningún texto: lo que ya ha visto la persona no se puede retirar.
        """
        cuerpo = {**_cuerpo(self._modelo, peticion), "stream": True, "stream_options": {"include_usage": True}}
        inicio = time.perf_counter()
        emitido = False

        def emitir(trozo: str) -> None:
            nonlocal emitido
            emitido = True
            al_texto(trozo)

        try:
            for intento in Retrying(
                stop=stop_after_attempt(self._intentos),
                wait=wait_exponential_jitter(multiplier=self._pausa, max=4, jitter=self._pausa),
                retry=retry_if_exception(lambda e: not emitido and _reintentable(e)),
                reraise=True,
            ):
                with intento:
                    with self._cliente.chat.completions.create(**cuerpo) as trozos:
                        return _juntar(trozos, self._modelo, emitir, inicio)
        except openai.RateLimitError as e:
            raise LLMNoDisponibleException(f"{self._modelo}: {_describir(e)}", _retry_after(e.response)) from e
        except openai.APIStatusError as e:
            if _reintentable(e):
                raise LLMNoDisponibleException(f"{self._modelo}: {_describir(e)}") from e
            raise PeticionLLMException(f"{self._modelo}: {_describir(e)}") from e
        except openai.APIConnectionError as e:  # también un corte a mitad del stream
            raise LLMNoDisponibleException(f"{self._modelo}: {_describir(e)}") from e
        raise AssertionError("inalcanzable")  # pragma: no cover


def _juntar(trozos, modelo: str, emitir: Callable[[str], None], inicio: float) -> RespuestaLLM:
    """Los trozos de un stream de Chat Completions, juntos. El texto y el razonamiento llegan como deltas que se
    concatenan; cada tool call, en trozos con su `index` (el id y el nombre en el primero, los argumentos repartidos)."""
    texto, razonamiento, final, servido = [], [], None, modelo
    llamadas: dict[int, dict] = {}
    uso = Uso()
    c: ChatCompletionChunk
    for c in trozos:
        servido = c.model or servido
        if c.usage is not None:  # el último trozo (include_usage): sin choices, con el uso de toda la respuesta
            uso = _uso(c)
        if not c.choices:
            continue
        eleccion = c.choices[0]
        delta = eleccion.delta
        if delta.content:
            texto.append(delta.content)
            emitir(delta.content)
        if extra := (delta.model_extra or {}).get("reasoning"):
            razonamiento.append(extra)
        for tc in delta.tool_calls or ():
            llamada = llamadas.setdefault(tc.index, {"id": "", "nombre": "", "argumentos": []})
            if tc.id:
                llamada["id"] = tc.id
            if tc.function and tc.function.name:
                llamada["nombre"] = tc.function.name
            if tc.function and tc.function.arguments:
                llamada["argumentos"].append(tc.function.arguments)
        final = eleccion.finish_reason or final
    tools = tuple(
        LlamadaTool(id=ll["id"], nombre=ll["nombre"], argumentos="".join(ll["argumentos"]) or "{}")
        for _, ll in sorted(llamadas.items())
    )
    motivo = MotivoFin.TOOLS if tools else MOTIVOS.get(final, MotivoFin.OTRO)
    return RespuestaLLM(
        mensaje=Mensaje.modelo(texto="".join(texto), llamadas=tools),
        motivo=motivo,
        uso=uso,
        modelo=servido,
        duracion_ms=int((time.perf_counter() - inicio) * 1000),
        razonamiento="".join(razonamiento),
    )


def _reintentable(e: BaseException) -> bool:
    if isinstance(e, openai.APIConnectionError):
        return True
    if not isinstance(e, openai.APIStatusError):
        return False
    return e.status_code in REINTENTABLES or e.status_code >= 500 or _error(e).get("code") in CODIGOS_REINTENTABLES


def _error(e: openai.APIStatusError) -> dict:
    """El objeto error del proveedor ({"message", "type", "code"}). El SDK lo deja en e.body."""
    cuerpo = e.body if isinstance(e.body, dict) else {}
    error = cuerpo.get("error", cuerpo)
    return error if isinstance(error, dict) else {}


def _describir(e: BaseException | None) -> str:
    """Una línea para el log y la excepción: el status y el código y el mensaje del proveedor, recortados."""
    if isinstance(e, openai.APIStatusError):
        error = _error(e)
        codigo = error.get("code") or error.get("type") or ""
        return f"{e.status_code} {codigo} {str(error.get('message', ''))[:200]}".strip()
    return type(e).__name__


def _retry_after(respuesta: httpx2.Response) -> float | None:
    try:
        return float(respuesta.headers["retry-after"])
    except (KeyError, ValueError):
        return None


# ── De nuestros tipos a los de Chat Completions ──
def _cuerpo(modelo: str, p: PeticionLLM) -> dict:
    mensajes = [{"role": "system", "content": p.sistema}] if p.sistema else []
    for m in p.mensajes:
        mensajes.extend(_mensajes(m))
    cuerpo: dict = {"model": modelo, "messages": mensajes}
    if p.tools:
        cuerpo["tools"] = [
            {
                "type": "function",
                "function": {"name": t.nombre, "description": t.descripcion, "parameters": t.parametros},
            }
            for t in p.tools
        ]
        cuerpo["tool_choice"] = "auto" if p.usar_tools else "none"
    if p.esquema:
        cuerpo["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": p.esquema.nombre, "schema": p.esquema.esquema, "strict": p.esquema.estricto},
        }
    if p.temperatura is not None:
        cuerpo["temperature"] = p.temperatura
    if p.esfuerzo is not None:
        cuerpo["reasoning_effort"] = ESFUERZOS[p.esfuerzo]
    if p.max_tokens is not None:
        cuerpo["max_completion_tokens"] = p.max_tokens
    return cuerpo


def _mensajes(m: Mensaje) -> list[dict]:
    if m.rol == RolMensaje.USUARIO:
        return [{"role": "user", "content": m.texto}]
    if m.rol == RolMensaje.MODELO:
        mensaje: dict = {"role": "assistant", "content": m.texto or None}
        if m.llamadas:
            mensaje["tool_calls"] = [
                {"id": ll.id, "type": "function", "function": {"name": ll.nombre, "arguments": ll.argumentos}}
                for ll in m.llamadas
            ]
        return [mensaje]
    # RolMensaje.TOOL: en Chat Completions, un mensaje "tool" por resultado, con el id de su llamada
    return [{"role": "tool", "tool_call_id": r.llamada_id, "content": r.contenido} for r in m.resultados]


# ── De la respuesta de Chat Completions a la nuestra ──
def _respuesta(c: ChatCompletion, modelo: str, duracion_ms: int) -> RespuestaLLM:
    eleccion = c.choices[0]
    m = eleccion.message
    llamadas = tuple(
        LlamadaTool(id=tc.id, nombre=tc.function.name, argumentos=tc.function.arguments or "{}")
        for tc in m.tool_calls or ()
        if tc.type == "function"
    )
    motivo = MotivoFin.TOOLS if llamadas else MOTIVOS.get(eleccion.finish_reason, MotivoFin.OTRO)
    # Groq devuelve el razonamiento de los gpt-oss en message.reasoning: un campo que no es del estándar (el SDK lo
    # guarda en model_extra). Otros proveedores no lo mandan: queda vacío.
    razonamiento = (m.model_extra or {}).get("reasoning") or ""
    return RespuestaLLM(
        mensaje=Mensaje.modelo(texto=m.content or "", llamadas=llamadas),
        motivo=motivo,
        uso=_uso(c),
        modelo=c.model or modelo,
        duracion_ms=duracion_ms,
        razonamiento=razonamiento,
    )


def _uso(c: ChatCompletion | ChatCompletionChunk) -> Uso:
    u = c.usage
    if u is None:  # algún proveedor compatible no lo manda: mejor 0 que inventarlo
        return Uso()
    detalle_salida, detalle_entrada = u.completion_tokens_details, u.prompt_tokens_details
    return Uso(
        entrada=u.prompt_tokens,
        salida=u.completion_tokens,
        razonamiento=(detalle_salida.reasoning_tokens or 0) if detalle_salida else 0,
        cache=(detalle_entrada.cached_tokens or 0) if detalle_entrada else 0,
    )


def a_json(peticion: PeticionLLM, modelo: str) -> str:
    """El cuerpo que se mandaría, legible (manage.py probar_llm --ver-peticion). La clave no: va en una cabecera."""
    return json.dumps(_cuerpo(modelo, peticion), ensure_ascii=False, indent=2)
