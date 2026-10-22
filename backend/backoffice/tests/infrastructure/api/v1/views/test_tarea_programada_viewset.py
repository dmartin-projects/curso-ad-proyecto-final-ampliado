"""Las tareas de Celery Beat (módulos 79 y 88)."""

import pytest
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from backoffice.tests.infrastructure.api.v1.conftest import URL
from conftest import UsuarioFactory

pytestmark = pytest.mark.django_db


def test_pausar_una_tarea_programada(soporte, superusuario):
    tarea = PeriodicTask.objects.create(
        name="informes-mensuales",
        task="informes.tasks.generar_informes_mensuales",
        crontab=CrontabSchedule.objects.create(minute="0", hour="7", day_of_month="1"),
    )
    assert soporte.get(URL + "tareas/").data[0]["name"] == "informes-mensuales"
    assert soporte.patch(URL + f"tareas/{tarea.pk}/", {"enabled": False}).status_code == 403  # Soporte solo mira
    assert superusuario.patch(URL + f"tareas/{tarea.pk}/", {"enabled": False}).data["enabled"] is False


def test_si_falla_la_auditoria_no_se_guarda_el_cambio(superusuario, monkeypatch):
    usuario = UsuarioFactory()
    tarea = PeriodicTask.objects.create(
        name="informes-mensuales",
        task="informes.tasks.generar_informes_mensuales",
        crontab=CrontabSchedule.objects.create(minute="0", hour="7", day_of_month="1"),
    )

    def auditoria_caida(*args, **kwargs):
        raise RuntimeError("auditoría caída")

    monkeypatch.setattr("backoffice.infrastructure.api.v1.views.usuario_soporte_viewset.registrar", auditoria_caida)
    monkeypatch.setattr("backoffice.infrastructure.api.v1.views.tarea_programada_viewset.registrar", auditoria_caida)
    assert superusuario.patch(URL + f"usuarios/{usuario.pk}/", {"is_active": False}).status_code == 500
    assert superusuario.patch(URL + f"tareas/{tarea.pk}/", {"enabled": False}).status_code == 500
    # los dos perform_update son atómicos: sin su registro de auditoría, el cambio no queda
    usuario.refresh_from_db()
    tarea.refresh_from_db()
    assert usuario.is_active and tarea.enabled
