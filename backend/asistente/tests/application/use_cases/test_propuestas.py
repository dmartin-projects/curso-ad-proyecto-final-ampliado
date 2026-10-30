"""Módulo 97: confirmar una propuesta ejecuta el use case de la app dueña con el Actor de QUIEN CONFIRMA."""

from datetime import timedelta

import pytest

from asistente.application.confirmar_propuesta_use_case.confirmar_propuesta_use_case import ConfirmarPropuestaUseCase
from asistente.application.confirmar_propuesta_use_case.dtos.confirmar_propuesta_input_dto import (
    ConfirmarPropuestaInputDTO,
)
from asistente.application.descartar_propuesta_use_case.descartar_propuesta_use_case import DescartarPropuestaUseCase
from asistente.application.descartar_propuesta_use_case.dtos.descartar_propuesta_input_dto import (
    DescartarPropuestaInputDTO,
)
from asistente.domain.bo.propuesta import Propuesta
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from asistente.domain.exceptions.propuesta_no_encontrada_exception import PropuestaNoEncontradaException
from asistente.domain.exceptions.propuesta_ya_resuelta_exception import PropuestaYaResueltaException
from asistente.tests.fakes.ejecutor_de_propuestas_fake import EjecutorDePropuestasFake
from asistente.tests.fakes.mundo import ANA, HOGAR, reloj
from asistente.tests.fakes.propuesta_command_repository_fake import PropuestaCommandRepositoryFake
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.exceptions.validacion_exception import ValidacionException
from core.domain.vo.actor import Actor
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake


def montar(fallo=None, creada=None):
    propuestas, ejecutor = PropuestaCommandRepositoryFake(), EjecutorDePropuestasFake(fallo)
    p = Propuesta(1, ANA, HOGAR, TipoPropuesta.MOVIMIENTO, "Gasto", {"importe": "-3.50"}, creada or reloj().ahora())
    propuestas.guardar(p)
    caso = ConfirmarPropuestaUseCase(
        propuestas=propuestas, ejecutor=ejecutor, reloj=reloj(), uow=UnidadDeTrabajoFake(propuestas)
    )
    return caso, propuestas, ejecutor, p.id


def test_se_ejecuta_una_vez_con_el_rol_de_quien_confirma():
    caso, propuestas, ejecutor, pid = montar()
    r = caso.ejecutar(ConfirmarPropuestaInputDTO(HOGAR, Actor(ANA, Rol.MIEMBRO), pid))
    assert (r.estado, r.resultado) == ("confirmada", {"movimiento_id": 101})
    assert ejecutor.ejecutadas == [(pid, Actor(ANA, Rol.MIEMBRO))] and propuestas.bloqueadas == [pid]
    with pytest.raises(PropuestaYaResueltaException):  # el doble clic
        caso.ejecutar(ConfirmarPropuestaInputDTO(HOGAR, Actor(ANA, Rol.MIEMBRO), pid))
    assert len(ejecutor.ejecutadas) == 1


def test_un_lector_no_apunta_ni_a_traves_del_asistente():
    caso, propuestas, ejecutor, pid = montar()
    with pytest.raises(SinPermisoException):
        caso.ejecutar(ConfirmarPropuestaInputDTO(HOGAR, Actor(ANA, Rol.LECTOR), pid))
    assert propuestas.obtener(ANA, HOGAR, pid).estado == "pendiente"  # sigue ahí, por si se la confirma otro día


def test_si_la_app_duena_la_rechaza_sigue_pendiente():
    caso, propuestas, _, pid = montar(fallo=ValidacionException("La categoría ya no existe."))
    with pytest.raises(ValidacionException):
        caso.ejecutar(ConfirmarPropuestaInputDTO(HOGAR, Actor(ANA, Rol.ADMIN), pid))
    assert propuestas.obtener(ANA, HOGAR, pid).estado == "pendiente"


def test_ni_la_de_ayer_ni_la_de_otro():
    caso, _, ejecutor, pid = montar(creada=reloj().ahora() - timedelta(days=2))
    with pytest.raises(PropuestaYaResueltaException, match="caducado"):
        caso.ejecutar(ConfirmarPropuestaInputDTO(HOGAR, Actor(ANA, Rol.ADMIN), pid))
    with pytest.raises(PropuestaNoEncontradaException):
        caso.ejecutar(ConfirmarPropuestaInputDTO(HOGAR, Actor(99, Rol.ADMIN), pid))
    assert ejecutor.ejecutadas == []


def test_descartar():
    _, propuestas, _, pid = montar()
    r = DescartarPropuestaUseCase(propuestas=propuestas, uow=UnidadDeTrabajoFake(propuestas)).ejecutar(
        DescartarPropuestaInputDTO(HOGAR, Actor(ANA, Rol.LECTOR), pid)
    )
    assert r.estado == "descartada"
