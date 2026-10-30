import asyncio
import json

from django.conf import settings
from django.conf.urls.static import static
from django.core import mail
from django.http import JsonResponse, StreamingHttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .urls import urlpatterns as urls_normales


@csrf_exempt
def ia_falsa(request):
    """Responde siempre el mismo ticket (lo que leería un modelo de verdad de la foto de ejemplo)."""
    datos = {
        "comercio": "Mercadona",
        "nif": "",
        "fecha": "2026-10-12",
        "total": 4.85,
        "moneda": "EUR",
        "categoria": "Supermercado",
        "lineas": [{"descripcion": "Leche", "cantidad": 1, "precio_unitario": 4.85}],
        "confianza": 0.95,
    }
    return JsonResponse({"choices": [{"message": {"role": "assistant", "content": json.dumps(datos)}}]})


def _respuesta_del_llm(cuerpo: dict) -> tuple[str, dict | None]:
    """Módulo 97: lo que contestaría un modelo, según la petición: (texto, tool call o None). Determinista y sin red:
    el E2E prueba la aplicación (streaming, propuestas, gráficos), no al modelo (eso son las evals, módulo 103)."""
    mensajes = cuerpo["messages"]
    ultimo = mensajes[-1]
    if "response_format" in cuerpo:  # estructurar.py: la respuesta en JSON, con preguntas de seguimiento
        respuesta = next(m["content"] for m in reversed(mensajes) if m["role"] == "assistant")
        return json.dumps({"texto": respuesta, "cifras": [], "seguimiento": ["¿Y en agosto?"]}), None
    if not cuerpo.get("tools"):  # el título (el modelo auxiliar)
        return "Gastos del mes", None
    if ultimo["role"] == "tool":
        resultado = json.loads(ultimo["content"])
        if "grafico" in resultado:
            return "Aquí tienes la evolución de los últimos meses.", None
        if "propuesta" in resultado:
            return "Te lo dejo preparado: confírmalo abajo.", None
        if "recordado" in resultado:  # módulo 99
            return "Anotado: lo tendré en cuenta en las próximas conversaciones.", None
        if "error" in resultado:
            return f"No he podido: {resultado['error']}", None
        return f"En {resultado['mes']} gastasteis {resultado['gastos'].replace('.', ',')} €.", None
    pregunta = ultimo["content"].lower()
    if "dibuja" in pregunta:
        argumentos = {
            "tipo": "lineas",
            "titulo": "Gastos de los últimos meses",
            "fuente": "tendencia",
            "argumentos": {"meses": 3},
        }
        return "", {"name": "grafico", "arguments": json.dumps(argumentos)}
    if pregunta.startswith("recuerda que"):  # módulo 99
        texto = ultimo["content"][len("recuerda que ") :].strip().rstrip(".")
        return "", {"name": "recordar", "arguments": json.dumps({"texto": texto[0].upper() + texto[1:] + "."})}
    if "apunta" in pregunta:
        argumentos = {"importe": "3.50", "concepto": "Churros", "cuenta": "Cuenta común"}
        return "", {"name": "proponer_movimiento", "arguments": json.dumps(argumentos)}
    if "lenta" in pregunta:  # para probar "Detener": una respuesta que tarda en llegar entera
        return "Esta respuesta llega muy despacio, palabra a palabra, " * 8, None
    mes = "2026-08" if "agosto" in pregunta else None
    return "", {"name": "resumen_mes", "arguments": json.dumps({"mes": mes} if mes else {})}


@csrf_exempt
def llm_falso(request):
    """Módulo 97: el LLM del asistente en los E2E, con la forma de Chat Completions (también en streaming)."""
    cuerpo = json.loads(request.body)
    texto, llamada = _respuesta_del_llm(cuerpo)
    tool_calls = [{"index": 0, "id": "llamada-1", "type": "function", "function": llamada}] if llamada else None
    fin = "tool_calls" if llamada else "stop"
    uso = {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}
    base = {"id": "e2e", "created": 1, "model": cuerpo["model"]}
    if not cuerpo.get("stream"):
        mensaje = {"role": "assistant", "content": texto or None, **({"tool_calls": tool_calls} if llamada else {})}
        eleccion = {"index": 0, "message": mensaje, "finish_reason": fin}
        return JsonResponse({**base, "object": "chat.completion", "choices": [eleccion], "usage": uso})

    # Asíncrono: con ASGI (daphne), Django consume un generador SÍNCRONO entero antes de enviar nada (y avisa)
    async def trozos():
        def trozo(delta, final=None, usage=None):
            elecciones = [] if delta is None else [{"index": 0, "delta": delta, "finish_reason": final}]
            datos = {**base, "object": "chat.completion.chunk", "choices": elecciones, "usage": usage}
            return f"data: {json.dumps(datos)}\n\n"

        if llamada:
            yield trozo({"role": "assistant", "tool_calls": tool_calls})
        lento = "despacio" in texto
        for palabra in texto.split(" ") if texto else []:
            yield trozo({"content": palabra + " "})
            if lento:
                await asyncio.sleep(0.4)
        yield trozo({}, final=fin)
        yield trozo(None, usage=uso)
        yield "data: [DONE]\n\n"

    return StreamingHttpResponse(trozos(), content_type="text/event-stream")


def correos(request):
    """Los correos que ha "enviado" este proceso (backend de email en memoria): el E2E lee el enlace como la persona.

    GET /e2e/correos?para=ana@example.com → {"correos": [{"asunto": …, "cuerpo": …}, …]}, del más antiguo al último.
    """
    para = request.GET.get("para", "")
    enviados = getattr(mail, "outbox", [])  # la lista la crea el backend locmem con el primer envío
    return JsonResponse({"correos": [{"asunto": m.subject, "cuerpo": m.body} for m in enviados if para in m.to]})


@csrf_exempt
def envejecer_sesiones(request):
    """Módulo 92: que las sesiones abiertas se autenticaran hace una hora (el step-up pide 5 minutos). En un E2E no se
    puede esperar, y el momento está en el servidor, no en el navegador."""
    from datetime import timedelta

    from django.utils import timezone

    from usuarios.models import Sesion

    n = Sesion.objects.filter(cerrada__isnull=True).update(autenticada=timezone.now() - timedelta(hours=1))
    return JsonResponse({"envejecidas": n})


@csrf_exempt
def gastar_cuota(request):
    """Módulo 98: POST gasta la cuota del día de todos los miembros (una fila del libro de cuentas con los tokens del
    plan); DELETE la devuelve. Gastarla de verdad serían decenas de preguntas."""
    from datetime import timedelta

    from django.utils import timezone

    from asistente.models import Consumo
    from hogares.models import Membresia

    if request.method == "DELETE":
        return JsonResponse({"borrados": Consumo.objects.filter(modelo="e2e").delete()[0]})
    tokens = settings.ASISTENTE_PLANES["basico"]["tokens_dia_persona"]
    ahora = timezone.now() - timedelta(minutes=1)
    filas = [
        Consumo(usuario_id=m.usuario_id, hogar_id=m.hogar_id, canal="chat", modelo="e2e", tokens_entrada=tokens,
                tokens_salida=0, coste=0, momento=ahora)
        for m in Membresia.objects.all()
    ]  # fmt: skip
    return JsonResponse({"gastadas": len(Consumo.objects.bulk_create(filas))})


# en E2E los archivos están en disco (en producción, URLs firmadas de S3/R2): Django los sirve con DEBUG
urlpatterns = [
    path("e2e/ia/chat/completions", ia_falsa),
    path("e2e/llm/chat/completions", llm_falso),  # módulo 97
    path("e2e/correos", correos),
    path("e2e/sesiones/envejecer", envejecer_sesiones),
    path("e2e/asistente/cuota", gastar_cuota),  # módulo 98
    *urls_normales,
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
