"""La coordinadora de Celery Beat del día 1 (módulos 26, 78 y 88)."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings

from config.celery import app
from conftest import HogarFactory
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual
from informes.infrastructure.tasks.generar_informes_mensuales_task import generar_informes_mensuales

pytestmark = pytest.mark.django_db
OCT = date(2026, 10, 1)


def test_la_tarea_de_beat_genera_el_mes_anterior_una_sola_vez(hogar_con_datos, time_machine):
    hogar, _ = hogar_con_datos
    HogarFactory()  # sin movimientos en octubre: no recibe informe
    time_machine.move_to(datetime(2026, 11, 1, 7, 0, tzinfo=ZoneInfo("Europe/Madrid")))

    assert generar_informes_mensuales() == 1
    assert InformeMensual.objects.get().mes == OCT
    assert generar_informes_mensuales() == 0  # relanzarla no duplica nada


def test_las_tareas_programadas_existen():
    """Un error tipográfico en CELERY_BEAT_SCHEDULE solo se notaría el día 1 a las 7:00…"""
    app.loader.import_default_modules()  # autodiscover_tasks es perezoso: importa los tasks.py como el worker
    for entrada in settings.CELERY_BEAT_SCHEDULE.values():
        assert entrada["task"] in app.tasks
