"""Generar un informe: el PDF se guarda, se avisa y se envía; el reemplazado se borra (módulos 78 y 88)."""

from datetime import date

import pytest
from django.core import mail

from core.domain.vo.mes import Mes
from informes.application.generar_informe_use_case.dtos.generar_informe_input_dto import GenerarInformeInputDTO
from informes.infrastructure import container
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual
from notificaciones.models import Notificacion

pytestmark = pytest.mark.django_db
OCT = date(2026, 10, 1)


def test_generar_guarda_notifica_y_envia_por_email(hogar_con_datos, django_capture_on_commit_callbacks):
    hogar, roles = hogar_con_datos

    with django_capture_on_commit_callbacks(execute=True):
        informe = InformeMensual.objects.get(
            pk=container.generar_informe().ejecutar(GenerarInformeInputDTO(hogar.pk, Mes.de(OCT))).id
        )

    assert informe.tamano > 1000 and informe.archivo.name.startswith(f"informes/{hogar.pk}/2026-10-")
    assert Notificacion.objects.filter(tipo="informe_listo").count() == 3  # admin, miembro y lector
    assert len(mail.outbox) == 3
    correo = mail.outbox[0]
    assert correo.subject == "Tu informe de 10/2026 · Piso Ruzafa"
    assert correo.attachments[0][0] == "gastos-2026-10.pdf" and correo.attachments[0][2] == "application/pdf"
    assert "Ver en la app" in correo.alternatives[0][0] and "1\xa0254,50 €" in correo.body


def test_regenerar_reemplaza_el_archivo(hogar_con_datos, django_capture_on_commit_callbacks):
    hogar, _ = hogar_con_datos
    with django_capture_on_commit_callbacks(execute=True):
        primero = InformeMensual.objects.get(
            pk=container.generar_informe().ejecutar(GenerarInformeInputDTO(hogar.pk, Mes.de(OCT), enviar=False)).id
        )
    viejo = primero.archivo.name
    with django_capture_on_commit_callbacks(execute=True):
        segundo = InformeMensual.objects.get(
            pk=container.generar_informe().ejecutar(GenerarInformeInputDTO(hogar.pk, Mes.de(OCT), enviar=False)).id
        )

    assert segundo.pk == primero.pk and segundo.archivo.name != viejo
    assert not segundo.archivo.storage.exists(viejo)
    assert len(mail.outbox) == 0
