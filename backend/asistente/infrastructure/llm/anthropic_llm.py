# asistente/infrastructure/llm/anthropic_llm.py — ILLM con Claude, el SDK oficial `anthropic` (módulo 106)
"""El mismo port que Groq (módulo 93), otra API: la Messages API de Anthropic. Lo que cambia, todo aquí dentro:

    Chat Completions (Groq)                  Messages (Anthropic)
    mensaje "system"                         `system`, fuera de los mensajes (con su cache_control)
    tool_calls con argumentos en TEXTO       bloques `tool_use` con `input` ya como objeto
    un mensaje "tool" por resultado          bloques `tool_result` en UN mensaje del usuario, primero
    finish_reason                            stop_reason (end_turn, tool_use, max_tokens, refusal…)
    response_format (sin tools en Groq)      output_config.format, y SÍ se puede junto a las tools
    reasoning_effort                         output_config.effort
    caché implícita del prefijo              cache_control: el prefijo cacheado se marca (y se paga distinto)

El agent loop, las tools, el prompt y las evals no se enteran: es lo que prometía el port.
"""

import json
import time
from collections.abc import Callable

import anthropic
from anthropic import Anthropic

from asistente.application.ports.i_llm import ILLM
from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.domain.vo.uso import Uso

MAX_TOKENS = 4096  # Anthropic lo exige en cada petición (Chat Completions, no)
MOTIVOS = {
    "end_turn": MotivoFin.FIN,
    "stop_sequence": MotivoFin.FIN,
    "pause_turn": MotivoFin.FIN,  # solo con tools de servidor de Anthropic (no las usamos)
    "tool_use": MotivoFin.TOOLS,
    "max_tokens": MotivoFin.LIMITE_TOKENS,
    "model_context_window_exceeded": MotivoFin.LIMITE_TOKENS,
    "refusal": MotivoFin.BLOQUEADA,
}
ESFUERZOS = {
    EsfuerzoDeRazonamiento.BAJO: "low",
    EsfuerzoDeRazonamiento.MEDIO: "medium",
    EsfuerzoDeRazonamiento.ALTO: "high",
}
EFIMERA = {"type": "ephemeral"}  # 5 minutos (el agent loop vuelve en segundos)


class AnthropicLLM(ILLM):
    def __init__(self, *, cliente: Anthropic, modelo: str, cache: bool = True):
        self.cliente, self._modelo, self.cache = cliente, modelo, cache

    @property
    def modelo(self) -> str:
        return self._modelo

    def generar(self, peticion: PeticionLLM) -> RespuestaLLM:
        inicio = time.monotonic()
        with _errores(self._modelo):
            m = self.cliente.messages.create(**cuerpo(self._modelo, peticion, self.cache))
        return respuesta(m, self._modelo, int((time.monotonic() - inicio) * 1000))

    def generar_en_streaming(self, peticion: PeticionLLM, al_texto: Callable[[str], None]) -> RespuestaLLM:
        inicio = time.monotonic()
        with _errores(self._modelo), self.cliente.messages.stream(**cuerpo(self._modelo, peticion, self.cache)) as s:
            for trozo in s.text_stream:  # solo el texto visible: el tool_use llega entero al final
                al_texto(trozo)
            m = s.get_final_message()
        return respuesta(m, self._modelo, int((time.monotonic() - inicio) * 1000))

    def contar_tokens(self, peticion: PeticionLLM) -> int:
        """Ejercicio 2: los tokens de entrada de una petición con el tokenizer del modelo, sin generar nada (gratis, con
        su propio límite de peticiones por minuto). La documentación lo llama estimación: puede diferir un poco de lo que
        cuente la llamada. `estimar_tokens` (módulo 96) cuenta caracteres, sin red; esto, el proveedor."""
        c = cuerpo(self._modelo, peticion, cache=False)
        aceptados = {
            k: c[k] for k in ("model", "system", "messages", "tools", "tool_choice", "output_config") if k in c
        }
        with _errores(self._modelo):
            return self.cliente.messages.count_tokens(**aceptados).input_tokens


class _errores:
    """Los errores del SDK, traducidos a los del port (como en OpenAICompatibleLLM). Los reintentos los hace el SDK
    (max_retries del cliente, con su espera exponencial y el retry-after de Anthropic); lo que llega aquí ya ha
    agotado los suyos."""

    def __init__(self, modelo: str):
        self.modelo = modelo

    def __enter__(self):
        return self

    def __exit__(self, tipo, e, tb):
        if e is None:
            return False
        if isinstance(e, anthropic.RateLimitError):
            espera = e.response.headers.get("retry-after")
            raise LLMNoDisponibleException(f"{self.modelo}: 429", float(espera) if espera else None) from e
        if isinstance(e, anthropic.APIStatusError):
            if e.status_code >= 500:  # 529 (overloaded) incluido
                raise LLMNoDisponibleException(f"{self.modelo}: {e.status_code}") from e
            raise PeticionLLMException(f"{self.modelo}: {e.status_code}") from e
        if isinstance(e, anthropic.APIConnectionError):
            raise LLMNoDisponibleException(f"{self.modelo}: sin conexión") from e
        return False


# ── De nuestra petición a la Messages API ──
def cuerpo(modelo: str, p: PeticionLLM, cache: bool = True) -> dict:
    c: dict = {"model": modelo, "max_tokens": p.max_tokens or MAX_TOKENS, "messages": mensajes(p.mensajes)}
    if p.sistema:
        bloque = {"type": "text", "text": p.sistema}
        if cache:  # tools + system: el prefijo fijo de cada vuelta. Un breakpoint aquí lo cachea entero
            bloque["cache_control"] = EFIMERA
        c["system"] = [bloque]
    if cache:  # caché automática: el breakpoint en el último bloque, que avanza con la conversación (y el bucle)
        c["cache_control"] = EFIMERA
    if p.tools:
        c["tools"] = [{"name": t.nombre, "description": t.descripcion, "input_schema": t.parametros} for t in p.tools]
        c["tool_choice"] = {"type": "auto" if p.usar_tools else "none"}
    configuracion = {}
    if p.esquema:  # con Claude, JSON y tools en la MISMA llamada (con Groq, no: módulo 96)
        configuracion["format"] = {"type": "json_schema", "schema": p.esquema.esquema}
    if p.esfuerzo is not None:
        configuracion["effort"] = ESFUERZOS[p.esfuerzo]
    if configuracion:
        c["output_config"] = configuracion
    if p.temperatura is not None:
        c["temperature"] = min(p.temperatura, 1.0)  # Anthropic va de 0 a 1
    return c


def mensajes(historial: tuple[Mensaje, ...]) -> list[dict]:
    salida: list[dict] = []
    for m in historial:
        if m.rol == RolMensaje.USUARIO:
            salida.append({"role": "user", "content": m.texto})
        elif m.rol == RolMensaje.MODELO:
            # El razonamiento firmado, primero y sin tocar: en un turno con tools, Claude lo necesita para seguir
            bloques: list[dict] = [json.loads(b) for b in m.opaco]
            bloques += [{"type": "text", "text": m.texto}] if m.texto else []
            bloques += [{"type": "tool_use", "id": ll.id, "name": ll.nombre, "input": _input(ll.argumentos)}
                        for ll in m.llamadas]  # fmt: skip
            salida.append({"role": "assistant", "content": bloques or [{"type": "text", "text": "…"}]})
        else:  # TOOL: todos los resultados de una vuelta en UN mensaje del usuario, en el orden de las llamadas
            salida.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": r.llamada_id,
                            "content": r.contenido,
                            **({"is_error": True} if r.es_error else {}),
                        }
                        for r in m.resultados
                    ],  # fmt: skip
                }
            )
    return salida


def _input(argumentos: str) -> dict:
    """Nuestro historial guarda los argumentos como TEXTO (como los escribió el modelo, módulo 93); Anthropic quiere un
    objeto. Unos argumentos rotos (de un turno que ya falló) van vacíos: el resultado de error explica el resto."""
    try:
        valor = json.loads(argumentos or "{}")
    except ValueError:
        return {}
    return valor if isinstance(valor, dict) else {}


# ── De la respuesta de Anthropic a la nuestra ──
def respuesta(m, modelo: str, duracion_ms: int) -> RespuestaLLM:
    texto, razonamiento, llamadas, opaco = [], [], [], []
    for b in m.content:
        if b.type == "text":
            texto.append(b.text)
        elif b.type in ("thinking", "redacted_thinking"):
            # Con Claude 5.5 el razonamiento va activado y, por defecto, sin texto (display "omitted"): llega su firma,
            # y hay que devolverlo entero y en orden con el tool_use que lo acompaña
            razonamiento.append(getattr(b, "thinking", "") or "")
            opaco.append(json.dumps(b.model_dump(exclude_none=True), ensure_ascii=False))
        elif b.type == "tool_use":
            llamadas.append(LlamadaTool(id=b.id, nombre=b.name, argumentos=json.dumps(b.input, ensure_ascii=False)))
    motivo = MotivoFin.TOOLS if llamadas else MOTIVOS.get(m.stop_reason, MotivoFin.OTRO)
    return RespuestaLLM(
        mensaje=Mensaje.modelo(texto="".join(texto), llamadas=tuple(llamadas), opaco=tuple(opaco)),
        motivo=motivo,
        uso=uso(m.usage),
        modelo=m.model or modelo,
        duracion_ms=duracion_ms,
        razonamiento="\n".join(r for r in razonamiento if r),
    )


def uso(u) -> Uso:
    """En Anthropic, `input_tokens` es solo lo que va DESPUÉS del último breakpoint: la entrada total es la suma de lo
    leído de la caché, lo escrito en ella y eso. Nuestro Uso.entrada es el total (como en Chat Completions)."""
    leidos = u.cache_read_input_tokens or 0
    escritos = u.cache_creation_input_tokens or 0
    detalle = getattr(u, "output_tokens_details", None)
    return Uso(
        entrada=u.input_tokens + leidos + escritos,
        salida=u.output_tokens,
        razonamiento=(detalle.thinking_tokens or 0) if detalle else 0,
        cache=leidos,
        cache_escrita=escritos,  # ejercicio 1
    )
