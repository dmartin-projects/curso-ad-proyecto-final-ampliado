"""Ejercicios 1 y 3 del 105, por la API: cancelar (202) y un segundo análisis mientras el primero está en marcha (409)."""

import uuid

import pytest
from django.core.cache import cache

from asistente.infrastructure.cache.control_de_analisis_en_cache import ControlDeAnalisisEnCache
from asistente.tests.infrastructure.api.v1.test_api_chat import url

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def cache_vacia():
    cache.clear()


def test_otro_mientras_el_primero_esta_en_marcha_409(casa, cliente, llm, django_capture_on_commit_callbacks):
    ana, hogar = casa
    with django_capture_on_commit_callbacks(execute=False):  # la tarea, encolada y sin empezar
        assert cliente(ana).post(url(hogar, "analisis"), {"tarea": str(uuid.uuid4())}).status_code == 202
    segundo = cliente(ana).post(url(hogar, "analisis"), {"tarea": str(uuid.uuid4())})
    assert (segundo.status_code, segundo.json()["type"].rsplit("/", 1)[-1]) == (409, "analisis_en_curso")


def test_cancelar_marca_el_de_esa_persona(casa, cliente):
    ana, hogar = casa
    tarea = str(uuid.uuid4())
    assert cliente(ana).delete(url(hogar, "analisis", tarea)).status_code == 202
    assert ControlDeAnalisisEnCache().cancelado(ana.pk, tarea)
    assert cliente(ana).delete(url(hogar, "analisis", "no-es-un-uuid")).status_code == 404
