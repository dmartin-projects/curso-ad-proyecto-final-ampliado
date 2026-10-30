"""Módulo 99, ejercicio 2: manage.py ver_contexto, lo que viajaría en una conversación."""

from datetime import UTC, datetime
from io import StringIO

import pytest
from django.core.management import call_command

from conftest import HogarFactory, UsuarioFactory

pytestmark = pytest.mark.django_db


def test_ver_contexto_de_una_conversacion():
    from asistente.domain.bo.conversacion import Conversacion
    from asistente.domain.bo.recuerdo import Recuerdo
    from asistente.domain.vo.mensaje import Mensaje
    from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
    from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
        ConversacionCommandRepositoryORM,
    )
    from asistente.infrastructure.database.repositories.recuerdo_command_repository_orm import (
        RecuerdoCommandRepositoryORM,
    )
    from conftest import MembresiaFactory

    ana, casa = UsuarioFactory(email="ana@example.com"), HogarFactory()
    MembresiaFactory(usuario=ana, hogar=casa)
    repo = ConversacionCommandRepositoryORM()
    conversacion = Conversacion(ana.pk, casa.pk)
    repo.guardar(conversacion)
    ids = repo.anadir(
        conversacion.id,
        [
            MensajeDeConversacion(Mensaje.usuario("Vieja"), visible=True, texto="Vieja"),
            MensajeDeConversacion(Mensaje.modelo(texto="Respuesta vieja"), visible=True, texto="Respuesta vieja"),
            MensajeDeConversacion(Mensaje.usuario("¿Septiembre?"), visible=True, texto="¿Septiembre?"),
            MensajeDeConversacion(Mensaje.modelo(texto="776,59 €."), visible=True, texto="776,59 €."),
        ],
    )
    conversacion.resumir("Preguntó algo viejo.", ids[1])
    repo.guardar_resumen(conversacion)
    RecuerdoCommandRepositoryORM().guardar(Recuerdo(ana.pk, casa.pk, "Somos dos.", datetime(2026, 10, 1, tzinfo=UTC)))
    salida = StringIO()
    call_command(
        "ver_contexto", "--email", "ana@example.com", "--hogar", str(casa.pk), "--conversacion", str(conversacion.id),
        stdout=salida,
    )  # fmt: skip
    texto = salida.getvalue()
    assert "- Somos dos." in texto and "Preguntó algo viejo." in texto and "Vieja\n" not in texto
    assert "── usuario" in texto and "¿Septiembre?" in texto and "776,59 €." in texto
    assert texto.rstrip().endswith("tokens estimados]")
