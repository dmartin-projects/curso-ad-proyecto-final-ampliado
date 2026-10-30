"""Módulos 98 y 99: el libro de cuentas y los planes en PostgreSQL (las sumas de las cuotas y el informe por hogar) y
el resumen de una conversación."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.plan import Plan
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.database.repositories.consumo_query_service_orm import ConsumoQueryServiceORM
from asistente.infrastructure.database.repositories.consumo_repository_orm import ConsumoRepositoryORM
from asistente.infrastructure.database.repositories.plan_del_hogar_repository_orm import PlanDelHogarRepositoryORM
from conftest import HogarFactory, UsuarioFactory

pytestmark = pytest.mark.django_db
OCT = datetime(2026, 10, 15, 12, tzinfo=UTC)


def test_las_sumas_de_las_cuotas_y_el_informe():
    ana, luis = UsuarioFactory(), UsuarioFactory()
    casa, otro = HogarFactory(nombre="Casa"), HogarFactory(nombre="Piso")
    ConsumoRepositoryORM().anotar(
        [
            Consumo(ana.pk, casa.pk, CanalDeConsumo.CHAT, "a", Uso(1000, 100, cache=500), Decimal("0.0002"), OCT, 4),
            Consumo(ana.pk, casa.pk, CanalDeConsumo.TITULO, "b", Uso(50, 10), None, OCT),
            Consumo(luis.pk, casa.pk, CanalDeConsumo.CHAT, "a", Uso(300, 30), Decimal("0.0001"), OCT),
            Consumo(ana.pk, otro.pk, CanalDeConsumo.CHAT, "a", Uso(9, 9), Decimal("0.5"), OCT),
            Consumo(
                ana.pk, casa.pk, CanalDeConsumo.CHAT, "a", Uso(7, 7), Decimal("1"), datetime(2026, 9, 1, tzinfo=UTC)
            ),
        ]
    )
    q = ConsumoQueryServiceORM()
    assert q.tokens(ana.pk, casa.pk, datetime(2026, 10, 1, tzinfo=UTC)) == 1160  # la caché cuenta (está en la entrada)
    assert q.coste(casa.pk, datetime(2026, 10, 1, tzinfo=UTC)) == Decimal("0.0003")  # el sin precio no suma

    filas = q.por_hogar(datetime(2026, 10, 1, tzinfo=UTC), datetime(2026, 11, 1, tzinfo=UTC))
    assert [
        (f.hogar, f.modelo, f.llamadas, f.tokens_entrada, f.tokens_cache, f.coste, f.sin_precio) for f in filas
    ] == [
        ("Piso", "a", 1, 9, 0, Decimal("0.5"), 0),
        ("Casa", "a", 2, 1300, 500, Decimal("0.0003"), 0),
        ("Casa", "b", 1, 50, 0, Decimal("0"), 1),
    ]


def test_un_hogar_borrado_no_borra_lo_gastado():
    casa = HogarFactory()
    ConsumoRepositoryORM().anotar(
        [Consumo(UsuarioFactory().pk, casa.pk, CanalDeConsumo.CHAT, "a", Uso(1, 1), Decimal("0.1"), OCT)]
    )
    casa.delete()
    [fila] = ConsumoQueryServiceORM().por_hogar(datetime(2026, 10, 1, tzinfo=UTC), datetime(2026, 11, 1, tzinfo=UTC))
    assert (fila.hogar_id, fila.hogar, fila.coste) == (None, "(hogar borrado)", Decimal("0.1"))


def test_el_plan_basico_no_necesita_fila():
    casa, planes = HogarFactory(), PlanDelHogarRepositoryORM()
    assert planes.plan_de(casa.pk) == Plan.BASICO
    planes.asignar(casa.pk, Plan.PLUS)
    assert planes.plan_de(casa.pk) == Plan.PLUS
    planes.asignar(casa.pk, Plan.BASICO)
    assert planes.plan_de(casa.pk) == Plan.BASICO


def test_guardar_el_resumen_no_sube_la_conversacion_en_la_lista():  # módulo 99
    from asistente.domain.bo.conversacion import Conversacion
    from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
    from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
        ConversacionCommandRepositoryORM,
    )

    ana, casa = UsuarioFactory(), HogarFactory()
    repo, conversacion = ConversacionCommandRepositoryORM(), Conversacion(ana.pk, casa.pk)
    repo.guardar(conversacion)
    antes = ConversacionModel.objects.get(pk=conversacion.id).actualizado
    conversacion.resumir("Resumen.", 3)
    repo.guardar_resumen(conversacion)
    fila = ConversacionModel.objects.get(pk=conversacion.id)
    assert (fila.resumen, fila.resumido_hasta, fila.actualizado) == ("Resumen.", 3, antes)
    assert repo.obtener(ana.pk, casa.pk, conversacion.id).resumen == "Resumen."
