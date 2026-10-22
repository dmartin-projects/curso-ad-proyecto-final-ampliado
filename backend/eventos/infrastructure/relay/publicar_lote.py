# eventos/infrastructure/relay/publicar_lote.py — el relay del outbox: el use case con sus métricas (módulos 85 y 88)
from opentelemetry import metrics
from opentelemetry.instrumentation.utils import suppress_instrumentation

from eventos.application.publicar_pendientes_use_case.dtos.publicar_pendientes_input_dto import (
    PublicarPendientesInputDTO,
)
from eventos.infrastructure import container

medidor = metrics.get_meter("gastos.eventos")
publicados = medidor.create_counter(
    "gastos.eventos.publicados", unit="{evento}", description="Eventos publicados en Kafka"
)
retraso = medidor.create_histogram(
    "gastos.eventos.retraso",
    unit="s",
    description="Tiempo desde que se guarda el evento hasta que Kafka lo confirma",
    explicit_bucket_boundaries_advisory=[0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 300],
)


def publicar_lote(productor, *, tamano: int = 500, timeout: float = 30) -> int:
    """Publica hasta `tamano` eventos pendientes, en orden de id. Devuelve cuántos ha publicado."""
    # Sin trazas para las consultas del relay: el sondeo se repite cada 0,5 s y cada consulta sería una traza nueva
    # en Tempo (172.800 al día, que llenarían la búsqueda y esconderían las de las peticiones). Lo que importa
    # del relay son los spans "publish", que crea el broker (suppress_instrumentation no los afecta) y que cuelgan
    # de la petición que hizo el cambio.
    with suppress_instrumentation():
        lote = container.publicar_pendientes(productor, timeout=timeout).ejecutar(PublicarPendientesInputDTO(tamano))
    for p in lote.eventos:
        retraso.record((lote.cuando - p.creado).total_seconds(), {"topic": p.topic})
    publicados.add(len(lote.eventos))
    return len(lote.eventos)
