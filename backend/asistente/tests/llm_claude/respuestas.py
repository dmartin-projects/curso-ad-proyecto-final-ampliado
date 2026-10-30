# asistente/tests/llm_claude/respuestas.py — respuestas de la Messages API, como las documenta Anthropic (módulo 106)
"""Los tests del adapter no necesitan clave: van contra respuestas construidas con la forma de la documentación oficial
(platform.claude.com/docs: Messages, tool use, prompt caching, streaming). Son ejemplos de la forma, no mediciones: lo
que contesta la API de verdad lo dice una llamada con clave (test_evals_con_claude.py, opcional)."""

import json


def mensaje(contenido: list[dict], stop_reason: str, *, entrada=1200, salida=80, leidos=0, escritos=0) -> dict:
    return {
        "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
        "type": "message",
        "role": "assistant",
        "model": "claude-haiku-5-5",
        "content": contenido,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": entrada,
            "output_tokens": salida,
            "cache_creation_input_tokens": escritos,
            "cache_read_input_tokens": leidos,
        },
    }


def tool_use(nombre: str, entrada: dict, id_="toolu_01A09q90qw90lq917835lq9") -> dict:
    return {"type": "tool_use", "id": id_, "name": nombre, "input": entrada}


def texto(t: str) -> dict:
    return {"type": "text", "text": t}


def sse(eventos: list[tuple[str, dict]]) -> bytes:
    return "".join(f"event: {tipo}\ndata: {json.dumps(datos)}\n\n" for tipo, datos in eventos).encode()


def stream_de_texto(trozos: list[str]) -> bytes:
    """El streaming de una respuesta de texto: message_start, un bloque de texto en deltas, message_delta y stop."""
    inicio = mensaje([], None, salida=1)
    eventos = [
        ("message_start", {"type": "message_start", "message": inicio}),
        ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": texto("")}),
    ]
    eventos += [
        ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": t}})
        for t in trozos
    ]
    eventos += [("content_block_stop", {"type": "content_block_stop", "index": 0}),
                ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                                   "usage": {"output_tokens": 15}}),
                ("message_stop", {"type": "message_stop"})]  # fmt: skip
    return sse(eventos)
