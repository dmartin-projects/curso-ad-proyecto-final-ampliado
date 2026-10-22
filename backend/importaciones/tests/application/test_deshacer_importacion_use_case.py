"""DeshacerImportacionUseCase con los fakes (módulo 88)."""

import pytest

from core.domain.enums.accion import Accion as AccionAuditoria
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from importaciones.application.confirmar_importacion_use_case.dtos.confirmar_importacion_input_dto import (
    ConfirmarImportacionInputDTO,
)
from importaciones.application.deshacer_importacion_use_case.dtos.deshacer_importacion_input_dto import (
    DeshacerImportacionInputDTO,
)
from importaciones.application.finalizar_importacion_use_case.dtos.finalizar_importacion_input_dto import (
    FinalizarImportacionInputDTO,
)
from importaciones.application.importar_lote_use_case.dtos.importar_lote_input_dto import ImportarLoteInputDTO
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.tests.fakes.mundo import EXTRACTO, HOGAR, Mundo, actor, preparada

E = EstadoImportacion


def test_deshacer_borra_lo_creado_devuelve_lo_conciliado_y_audita():
    mundo = Mundo(EXTRACTO)
    imp = preparada(mundo)
    mundo.confirmar.ejecutar(ConfirmarImportacionInputDTO(HOGAR, actor(), imp.id))
    mundo.importar_lote.ejecutar(ImportarLoteInputDTO(imp.id, mundo.importaciones.filas_a_importar(imp.id)))
    mundo.finalizar.ejecutar(FinalizarImportacionInputDTO(imp.id))
    with pytest.raises(SinPermisoException):
        mundo.deshacer.ejecutar(DeshacerImportacionInputDTO(HOGAR, actor(Rol.MIEMBRO), imp.id))

    mundo.deshacer.ejecutar(DeshacerImportacionInputDTO(HOGAR, actor(Rol.ADMIN), imp.id))

    assert [m["huella"] for m in mundo.movimientos.movimientos.values()] == [""]  # solo queda el apuntado a mano
    [(accion, tipo, pk, usuario, cambios)] = mundo.auditoria.registros
    assert (accion, tipo, pk, cambios["estado"]) == (
        AccionAuditoria.MODIFICAR,
        "importaciones.importacion",
        imp.id,
        ["completada", "deshecha"],
    )
