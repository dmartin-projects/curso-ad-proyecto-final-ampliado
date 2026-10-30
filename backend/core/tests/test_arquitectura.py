"""Lo que la arquitectura promete y no comprueba import-linter (módulo 88): los nombres de las tareas y la alarma."""

import logging

import pytest
from django.utils.module_loading import import_string

from conftest import CuentaFactory, MovimientoFactory
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.infrastructure.signals.escritura_sin_caso_de_uso_exception import EscrituraSinCasoDeUsoException
from core.infrastructure.signals.red_de_seguridad import escrituras_directas
from hogares.application.eliminar_hogar_use_case.dtos.eliminar_hogar_input_dto import EliminarHogarInputDTO
from hogares.infrastructure import container as hogares

# Los nombres que viajan en los mensajes de Celery (y que usan CELERY_TASK_ROUTES y CELERY_BEAT_SCHEDULE).
CELERY = {
    "asistente.tasks.compactar_conversacion",  # módulo 99
    "core.tasks.limpiar_resultados_de_tareas",
    "eventos.tasks.limpiar_eventos_publicados",
    "finanzas.tasks.comprobar_presupuestos_tarea",
    "importaciones.tasks.analizar_importacion",
    "importaciones.tasks.importar_lote",
    "importaciones.tasks.finalizar_importacion",
    "importaciones.tasks.importacion_fallida",
    "informes.tasks.generar_informes_mensuales",
    "informes.tasks.generar_informe",
    "notificaciones.tasks.emitir_evento_hogar",
    "tickets.tasks.procesar_ticket",
}
# Las rutas que guarda la cola de django.tasks: se importan con import_string() en el worker.
DJANGO_TASKS = {
    "hogares.tasks.enviar_invitacion",
    "informes.tasks.enviar_informe",
    "notificaciones.tasks.enviar_email_notificacion",
    "usuarios.tasks.enviar_email_completar_registro",
    "usuarios.tasks.enviar_email_cuenta_existente",
    "usuarios.tasks.enviar_email_recuperacion",
}


@pytest.mark.django_db  # al cargar las tasks, el fixup de Django de Celery abre la conexión
def test_las_tareas_de_celery_conservan_su_nombre():
    from config.celery import app

    app.loader.import_default_modules()  # lo que hace el worker al arrancar (autodiscover_tasks)
    propias = {n for n in app.tasks if not n.startswith("celery.")}
    assert propias == CELERY


@pytest.mark.parametrize("ruta", sorted(DJANGO_TASKS))
def test_las_tareas_de_django_tasks_conservan_su_ruta(ruta):
    tarea = import_string(ruta)  # lo que hace el worker con la ruta guardada
    assert tarea.module_path == ruta  # y la que se guarda al encolar


def test_las_tareas_de_tickets_van_a_la_cola_ocr():
    from config.celery import app

    assert app.amqp.router.route({}, "tickets.tasks.procesar_ticket")["queue"].name == "ocr"
    assert app.amqp.router.route({}, "importaciones.tasks.importar_lote")["queue"].name == "default"


# ── La alarma: lo que tiene eventos solo se escribe con un use case ──
@pytest.mark.django_db
def test_guardar_un_movimiento_con_el_orm_salta():
    m = MovimientoFactory()  # las factories: datos de partida, dentro de escrituras_directas()
    m.concepto = "a mano"
    with pytest.raises(EscrituraSinCasoDeUsoException, match="sin use case"):
        m.save()


@pytest.mark.django_db
def test_en_produccion_solo_avisa(settings, caplog):
    settings.EXIGIR_CASOS_DE_USO = False
    m = MovimientoFactory()
    with caplog.at_level(logging.ERROR, logger="core.infrastructure.signals.red_de_seguridad"):
        m.delete()
    assert "sin use case" in caplog.text


@pytest.mark.django_db
def test_las_cascadas_y_los_datos_de_partida_no_saltan(hogar_con_roles):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)
    m = MovimientoFactory(cuenta=cuenta)
    with escrituras_directas():
        m.save()
    # borrar el hogar se lleva sus movimientos por CASCADE: no pasan por su use case, y no es un error
    hogares.eliminar_hogar().ejecutar(EliminarHogarInputDTO(hogar.pk, Actor(roles["admin"].pk, Rol.ADMIN)))
