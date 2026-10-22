"""SubirExtractoUseCase con los fakes (módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from importaciones.application.subir_extracto_use_case.dtos.subir_extracto_input_dto import SubirExtractoInputDTO
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.events.extracto_subido_event import ExtractoSubidoEvent
from importaciones.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from importaciones.tests.fakes.mundo import HOGAR, Mundo, actor

E = EstadoImportacion


def test_subir_exige_cuenta_del_hogar_y_un_miembro():
    mundo = Mundo()
    entrada = SubirExtractoInputDTO(HOGAR, actor(), 10, b"csv", "x.csv", "csv", "h1")
    imp = mundo.subir.ejecutar(entrada)
    assert (imp.estado, imp.subido_por_id) == (E.PENDIENTE, 7) and mundo.eventos.publicados == [
        ExtractoSubidoEvent(imp.id)
    ]
    with pytest.raises(CuentaNoEncontradaException):
        mundo.subir.ejecutar(SubirExtractoInputDTO(HOGAR, actor(), 20, b"csv", "x.csv", "csv", "h2"))
    with pytest.raises(SinPermisoException):
        mundo.subir.ejecutar(SubirExtractoInputDTO(HOGAR, actor(Rol.LECTOR), 10, b"csv", "x.csv", "csv", "h3"))
