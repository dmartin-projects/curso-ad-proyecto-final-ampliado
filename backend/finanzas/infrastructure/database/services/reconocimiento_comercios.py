# finanzas/infrastructure/database/services/reconocimiento_comercios.py — reconocer comercios con pg_trgm
# (módulos 72, 74, 87 y 88)
#
# Solo las usa finanzas, a través del port IReconocedorComercios (reconocedor_comercios_orm.py): los procesos
# (tickets, importaciones) apuntan sus movimientos con ApuntarMovimientosUseCase.
from django.contrib.postgres.search import TrigramSimilarity
from django.db import IntegrityError, transaction
from django.db.models import Count

from core.domain.services.normalizacion import normalizar
from finanzas.infrastructure.database.models.categoria_model import Categoria
from finanzas.infrastructure.database.models.comercio_model import Comercio
from finanzas.infrastructure.database.models.movimiento_model import Movimiento

SIMILITUD_MINIMA = 0.4


def reconocer_comercio(texto: str) -> Comercio | None:
    """El comercio conocido más parecido al texto ("MERCADONA S.A. 1234" → Mercadona), o None.

    El filtro `trigram_similar` (operador % de pg_trgm) es el que aprovecha el índice GIN del módulo 72;
    la anotación solo sirve para ordenar los candidatos.
    """
    normalizado = normalizar(texto)
    if not normalizado:
        return None
    return (
        Comercio.objects.filter(nombre_normalizado__trigram_similar=normalizado)
        .annotate(sim=TrigramSimilarity("nombre_normalizado", normalizado))
        .filter(sim__gte=SIMILITUD_MINIMA)
        .order_by("-sim")
        .first()
    )


def reconocer_o_crear_comercio(nombre: str, nif: str = "") -> Comercio | None:
    if not normalizar(nombre):
        return None
    if comercio := reconocer_comercio(nombre):
        return comercio
    try:
        with transaction.atomic():  # savepoint: si otro proceso lo crea a la vez, la restricción única salta
            return Comercio.objects.create(nombre=nombre.strip()[:120], nif=nif)
    except IntegrityError:
        return Comercio.objects.get(nombre_normalizado=normalizar(nombre))


def sugerir_categoria(hogar_id: int, comercio_id: int | None, nombre_sugerido: str = "") -> int | None:
    """1º lo que este hogar suele elegir para ese comercio; 2º la categoría que propone la IA (por su nombre)."""
    if comercio_id is not None:
        habitual = (
            Movimiento.objects.filter(
                hogar_id=hogar_id, comercio_id=comercio_id, categoria__isnull=False, revisado=True
            )
            .values("categoria")
            .annotate(veces=Count("id"))
            .order_by("-veces", "categoria")  # a igualdad de veces, siempre la misma (y el fake, igual)
            .first()
        )
        if habitual:
            return habitual["categoria"]
    if nombre_sugerido:
        return (
            Categoria.objects.filter(hogar_id=hogar_id, nombre__iexact=nombre_sugerido)
            .values_list("pk", flat=True)
            .first()
        )
    return None
