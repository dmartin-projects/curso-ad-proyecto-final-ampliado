"""Todos los fakes juntos y los use cases montados con ellos: el container.py de los tests (módulo 89).

Y los mensajes, como los que publica el relay de Django. Con esto se prueban los use cases sin PostgreSQL ni Kafka.
"""

import json
from datetime import UTC, datetime

from estadisticas.application.procesar_lote_use_case.dtos.procesar_lote_input_dto import ProcesarLoteInputDTO
from estadisticas.application.procesar_lote_use_case.procesar_lote_use_case import ProcesarLoteUseCase
from estadisticas.application.reconstruir_proyeccion_use_case.reconstruir_proyeccion_use_case import (
    ReconstruirProyeccionUseCase,
)
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO
from estadisticas.domain.enums.topic import Topic
from tests.fakes.aparcados_fake import AparcadosFake
from tests.fakes.grupo_de_consumidores_fake import GrupoDeConsumidoresFake
from tests.fakes.membresia_command_repository_fake import MembresiaCommandRepositoryFake
from tests.fakes.memoria import Memoria
from tests.fakes.movimiento_command_repository_fake import MovimientoCommandRepositoryFake
from tests.fakes.progreso_command_repository_fake import ProgresoCommandRepositoryFake
from tests.fakes.trazas_fake import TrazasFake
from tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake

MOV, MEMB = "gastos.movimientos", "gastos.membresias"
TOPICS = {MOV: Topic.MOVIMIENTOS, MEMB: Topic.MEMBRESIAS}


class Mundo:
    def __init__(self, *, dlq_caida: bool = False, con_consumidores: bool = False):
        self.memoria = Memoria()
        self.uow = UnidadDeTrabajoFake(self.memoria)
        self.movimientos = MovimientoCommandRepositoryFake(self.memoria)
        self.membresias = MembresiaCommandRepositoryFake(self.memoria)
        self.progreso = ProgresoCommandRepositoryFake(self.memoria)
        self.aparcados = AparcadosFake(caido=dlq_caida)
        self.trazas = TrazasFake()
        self.grupo = GrupoDeConsumidoresFake(con_consumidores=con_consumidores)

    def procesar_lote(self, trazas=None) -> ProcesarLoteUseCase:
        return ProcesarLoteUseCase(
            uow=self.uow,
            movimientos=self.movimientos,
            membresias=self.membresias,
            progreso=self.progreso,
            aparcados=self.aparcados,
            trazas=trazas or self.trazas,
            topics=TOPICS,
        )

    def reconstruir_proyeccion(self) -> ReconstruirProyeccionUseCase:
        return ReconstruirProyeccionUseCase(
            grupo=self.grupo,
            uow=self.uow,
            movimientos=self.movimientos,
            membresias=self.membresias,
            progreso=self.progreso,
        )


# ── Mensajes como los que publica el relay de Django ──
MARCA = datetime(2026, 10, 15, 12, 0, tzinfo=UTC)


def lote(mensajes: list[MensajeInputDTO]) -> ProcesarLoteInputDTO:
    return ProcesarLoteInputDTO(mensajes=mensajes)


def mensaje(topic: str, clave: str, valor: bytes | None, version: int, *, offset: int = 0, particion: int = 0,
            esquema: str = "1", **cabeceras) -> MensajeInputDTO:  # fmt: skip
    return MensajeInputDTO(
        topic=topic,
        particion=particion,
        offset=offset,
        clave=clave,
        valor=valor,
        marca=MARCA,
        cabeceras={"version": str(version), "esquema": esquema} | cabeceras,
    )


def movimiento(pk: int, importe: str = "-10.00", version: int = 1, **kw) -> MensajeInputDTO:
    datos = {"id": pk, "hogar_id": 1, "cuenta_id": 1, "fecha": "2026-10-01", "importe": importe,
             "categoria_id": None, "comercio_id": None, "origen": "manual", "revisado": True}  # fmt: skip
    return mensaje(MOV, str(pk), json.dumps(datos).encode(), version, **kw)


def borrado(pk: int, version: int, **kw) -> MensajeInputDTO:
    return mensaje(MOV, str(pk), None, version, **kw)


def membresia(hogar_id: int, usuario_id: int, rol: str = "lector", version: int = 1, **kw) -> MensajeInputDTO:
    valor = json.dumps({"hogar_id": hogar_id, "usuario_id": usuario_id, "rol": rol}).encode()
    return mensaje(MEMB, f"{hogar_id}:{usuario_id}", valor, version, **kw)
