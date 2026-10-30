# asistente/infrastructure/telemetria/instrumentos.py — las métricas del asistente (módulo 98)
"""Con los nombres de las convenciones semánticas GenAI de OpenTelemetry (gen_ai.*), para que cualquier panel, alerta
o herramienta que las conozca las entienda sin traducir. Son de estado "Development": pueden cambiar de nombre, y por
eso están TODAS aquí, en un archivo: si cambian, se cambia un sitio (y el panel de Grafana).

Lo nuestro, con nuestro prefijo (gastos.asistente.*): el coste y las preguntas por motivo.

En Prometheus (el receptor OTLP traduce: puntos → guiones bajos, `_total` en los contadores, la unidad `s` → `_seconds`,
las unidades entre llaves desaparecen):
    gen_ai_client_inference_duration_seconds_bucket        gen_ai_client_inference_usage_input_tokens_total
    gen_ai_client_inference_time_to_first_chunk_seconds_*  gen_ai_client_inference_usage_output_tokens_total
    gen_ai_invoke_agent_duration_seconds_*                 gen_ai_client_inference_usage_cache_read_input_tokens_total
    gen_ai_execute_tool_duration_seconds_*                 gen_ai_client_inference_usage_reasoning_output_tokens_total
    gastos_asistente_coste_usd_total                       gastos_asistente_preguntas_total
    gastos_asistente_cuota_agotada_total                   gastos_asistente_vueltas_bucket (ejercicio 3)
    gastos_asistente_tokens_por_pregunta_bucket (ejercicio 3)
"""

from opentelemetry import metrics

# Los de la especificación para la duración de una inferencia: de 10 ms a 82 s, doblando
CUBOS = [0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24, 20.48, 40.96, 81.92]

_medidor = metrics.get_meter("gastos.asistente")

duracion_inferencia = _medidor.create_histogram(
    "gen_ai.client.inference.duration",
    unit="s",
    description="Lo que tarda una llamada al modelo (entera: con streaming, hasta el último trozo)",
    explicit_bucket_boundaries_advisory=CUBOS,
)
primer_trozo = _medidor.create_histogram(
    "gen_ai.client.inference.time_to_first_chunk",
    unit="s",
    description="Lo que tarda en llegar el primer trozo de texto: lo que la persona espera mirando la pantalla",
    explicit_bucket_boundaries_advisory=CUBOS,
)
tokens_entrada = _medidor.create_counter(
    "gen_ai.client.inference.usage.input_tokens", unit="{token}", description="Tokens de entrada (con los de caché)"
)
tokens_salida = _medidor.create_counter(
    "gen_ai.client.inference.usage.output_tokens", unit="{token}", description="Tokens de salida (con el razonamiento)"
)
tokens_cache = _medidor.create_counter(
    "gen_ai.client.inference.usage.cache_read.input_tokens",
    unit="{token}",
    description="De la entrada, los servidos desde la caché del proveedor",
)
tokens_razonamiento = _medidor.create_counter(
    "gen_ai.client.inference.usage.reasoning.output_tokens",
    unit="{token}",
    description="De la salida, los de razonamiento",
)
duracion_agente = _medidor.create_histogram(
    "gen_ai.invoke_agent.duration",
    unit="s",
    description="Lo que tarda una pregunta entera (todas sus vueltas)",
    explicit_bucket_boundaries_advisory=CUBOS,
)
duracion_tool = _medidor.create_histogram(
    "gen_ai.execute_tool.duration",
    unit="s",
    description="Lo que tarda una tool",
    explicit_bucket_boundaries_advisory=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)
coste = _medidor.create_counter(
    "gastos.asistente.coste_usd",
    unit="{USD}",
    description="Coste estimado con la tabla de precios (ASISTENTE_PRECIOS), por modelo",
)
preguntas = _medidor.create_counter(
    "gastos.asistente.preguntas", unit="{pregunta}", description="Preguntas terminadas, por cómo terminaron"
)
inyecciones = _medidor.create_counter(  # ejercicio 1 del 102
    "gastos.asistente.inyecciones",
    unit="{texto}",
    description="Textos que el clasificador ha tomado por prompt injection, por origen (una tool, adjunto o pregunta)",
)
cuota_agotada = _medidor.create_counter(
    "gastos.asistente.cuota_agotada",
    unit="{pregunta}",
    description="Preguntas rechazadas por la cuota, por cuál (persona u hogar)",
)

# Ejercicio 3: comparar versiones del prompt con datos. Por pregunta y con la versión como etiqueta (pocos valores: las
# publicadas). Un cambio de prompt que ahorra una vuelta se ve aquí en un día, sin esperar a las evals del módulo 103
vueltas = _medidor.create_histogram(
    "gastos.asistente.vueltas",
    unit="{vuelta}",
    description="Llamadas al modelo por pregunta, por versión del prompt",
    explicit_bucket_boundaries_advisory=[1, 2, 3, 4, 5, 6, 7],
)
tokens_por_pregunta = _medidor.create_histogram(
    "gastos.asistente.tokens_por_pregunta",
    unit="{token}",
    description="Tokens (entrada + salida) de una pregunta entera, por versión del prompt",
    explicit_bucket_boundaries_advisory=[1000, 2000, 4000, 6000, 8000, 12000, 16000, 24000, 32000],
)
