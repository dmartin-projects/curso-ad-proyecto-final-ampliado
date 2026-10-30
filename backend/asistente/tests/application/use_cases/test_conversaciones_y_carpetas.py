"""Módulo 97: las conversaciones y las carpetas son de cada persona: lo de otro, en otro hogar o en otra carpeta,
no existe (404)."""

import pytest

from asistente.application.crear_carpeta_use_case.crear_carpeta_use_case import CrearCarpetaUseCase
from asistente.application.crear_carpeta_use_case.dtos.crear_carpeta_input_dto import CrearCarpetaInputDTO
from asistente.application.crear_conversacion_use_case.crear_conversacion_use_case import CrearConversacionUseCase
from asistente.application.crear_conversacion_use_case.dtos.crear_conversacion_input_dto import (
    CrearConversacionInputDTO,
)
from asistente.application.modificar_conversacion_use_case.dtos.modificar_conversacion_input_dto import (
    ModificarConversacionInputDTO,
)
from asistente.application.modificar_conversacion_use_case.modificar_conversacion_use_case import (
    ModificarConversacionUseCase,
)
from asistente.domain.exceptions.carpeta_no_encontrada_exception import CarpetaNoEncontradaException
from asistente.domain.exceptions.carpeta_repetida_exception import CarpetaRepetidaException
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.tests.fakes.carpeta_command_repository_fake import CarpetaCommandRepositoryFake
from asistente.tests.fakes.conversacion_command_repository_fake import ConversacionCommandRepositoryFake
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake

ANA, LUIS, HOGAR = Actor(7, Rol.LECTOR), Actor(8, Rol.ADMIN), 3


@pytest.fixture
def repos():
    conversaciones, carpetas = ConversacionCommandRepositoryFake(), CarpetaCommandRepositoryFake()
    uow = UnidadDeTrabajoFake(conversaciones, carpetas)
    return {"conversaciones": conversaciones, "carpetas": carpetas, "uow": uow}


def test_un_lector_tambien_chatea_y_ordena_sus_carpetas(repos):
    carpeta = CrearCarpetaUseCase(carpetas=repos["carpetas"], uow=repos["uow"]).ejecutar(
        CrearCarpetaInputDTO(HOGAR, ANA, " Viaje ")
    )
    c = CrearConversacionUseCase(**repos).ejecutar(CrearConversacionInputDTO(HOGAR, ANA, carpeta.id))
    assert (carpeta.nombre, c.carpeta_id, c.titulo) == ("Viaje", carpeta.id, "")


def test_dos_carpetas_con_el_mismo_nombre_no(repos):
    caso = CrearCarpetaUseCase(carpetas=repos["carpetas"], uow=repos["uow"])
    caso.ejecutar(CrearCarpetaInputDTO(HOGAR, ANA, "Viaje"))
    with pytest.raises(CarpetaRepetidaException):
        caso.ejecutar(CrearCarpetaInputDTO(HOGAR, ANA, "Viaje"))
    caso.ejecutar(CrearCarpetaInputDTO(HOGAR, LUIS, "Viaje"))  # la suya: es de otra persona


def test_ni_la_carpeta_ni_la_conversacion_de_otro(repos):
    de_luis = CrearCarpetaUseCase(carpetas=repos["carpetas"], uow=repos["uow"]).ejecutar(
        CrearCarpetaInputDTO(HOGAR, LUIS, "Suya")
    )
    with pytest.raises(CarpetaNoEncontradaException):
        CrearConversacionUseCase(**repos).ejecutar(CrearConversacionInputDTO(HOGAR, ANA, de_luis.id))
    suya = CrearConversacionUseCase(**repos).ejecutar(CrearConversacionInputDTO(HOGAR, LUIS))
    with pytest.raises(ConversacionNoEncontradaException):
        ModificarConversacionUseCase(**repos).ejecutar(
            ModificarConversacionInputDTO(HOGAR, ANA, suya.id, {"titulo": "x"})
        )


def test_renombrar_y_sacar_de_la_carpeta(repos):
    c = CrearConversacionUseCase(**repos).ejecutar(CrearConversacionInputDTO(HOGAR, ANA))
    r = ModificarConversacionUseCase(**repos).ejecutar(
        ModificarConversacionInputDTO(HOGAR, ANA, c.id, {"titulo": "Mi título", "carpeta_id": None})
    )
    assert (r.titulo, r.carpeta_id) == ("Mi título", None)
    assert repos["conversaciones"].obtener(7, HOGAR, c.id).titulo_manual


def test_borrar_una_conversacion_borra_sus_archivos(repos):
    """Las fotos adjuntas y los CSV exportados: datos del hogar que, sin la conversación, nada enseña ni borra."""
    from asistente.application.eliminar_conversacion_use_case.dtos.eliminar_conversacion_input_dto import (
        EliminarConversacionInputDTO,
    )
    from asistente.application.eliminar_conversacion_use_case.eliminar_conversacion_use_case import (
        EliminarConversacionUseCase,
    )
    from asistente.domain.vo.mensaje import Mensaje
    from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
    from asistente.tests.fakes.almacen_de_archivos_fake import AlmacenDeArchivosFake

    almacen = AlmacenDeArchivosFake()
    foto, csv = almacen.guardar("asistente/3", b"jpg"), almacen.guardar("asistente/3/exportaciones", b"csv")
    otra = almacen.guardar("asistente/3", b"de otra conversacion")
    c = CrearConversacionUseCase(**repos).ejecutar(CrearConversacionInputDTO(HOGAR, ANA, None))
    repos["conversaciones"].anadir(
        c.id,
        [
            MensajeDeConversacion(Mensaje.usuario("¿Y esto?"), visible=True, adjunto=foto, nombre_adjunto="t.jpg"),
            MensajeDeConversacion(Mensaje.modelo(texto="Ahí va."), visible=True, datos={"archivos": [{"ruta": csv}]}),
        ],
    )
    EliminarConversacionUseCase(conversaciones=repos["conversaciones"], almacen=almacen, uow=repos["uow"]).ejecutar(
        EliminarConversacionInputDTO(HOGAR, ANA, c.id)
    )
    assert list(almacen.archivos) == [otra]
