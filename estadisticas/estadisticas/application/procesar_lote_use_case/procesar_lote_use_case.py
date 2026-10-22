# estadisticas/application/procesar_lote_use_case/procesar_lote_use_case.py — aplicar un lote de mensajes a la
# proyección (módulo 89; la lógica, del módulo 85 y su ejercicio 3)
#
# Un lote, UNA transacción: los cambios y el progreso se confirman juntos. Lo normal es aplicar el lote entero de
# una vez (rápido). Solo si algún mensaje es venenoso se repite mensaje a mensaje, cada uno en un savepoint, para
# aparcar los malos y aplicar los buenos. Medido con 20.000 mensajes en el módulo 85: con savepoint siempre, 34 s;
# así, 21 s (el savepoint por mensaje cuesta un 60 %).
#
# Ni Kafka, ni SQLAlchemy, ni OpenTelemetry: todo llega por interfaces. Los offsets de Kafka los confirma el adapter
# de entrada DESPUÉS de que este use case haya confirmado su transacción.
import logging
from datetime import datetime

from estadisticas.application.ports.i_aparcados import IAparcados
from estadisticas.application.ports.i_trazas import ITrazas
from estadisticas.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from estadisticas.application.procesar_lote_use_case.dtos.procesar_lote_input_dto import ProcesarLoteInputDTO
from estadisticas.application.procesar_lote_use_case.i_procesar_lote_use_case import IProcesarLoteUseCase
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO
from estadisticas.domain.enums.resultado import Resultado
from estadisticas.domain.enums.topic import Topic
from estadisticas.domain.events.membresia_eliminada_event import MembresiaEliminadaEvent
from estadisticas.domain.events.membresia_guardada_event import MembresiaGuardadaEvent
from estadisticas.domain.events.movimiento_eliminado_event import MovimientoEliminadoEvent
from estadisticas.domain.events.movimiento_guardado_event import MovimientoGuardadoEvent
from estadisticas.domain.exceptions.evento_invalido_exception import EventoInvalidoException
from estadisticas.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from estadisticas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository
from estadisticas.domain.repositories.i_progreso_command_repository import IProgresoCommandRepository
from estadisticas.domain.services.interpretacion import interpretar

logger = logging.getLogger(__name__)


class _HayVenenososException(Exception):
    """Interna: el primer intento ha encontrado un venenoso y hay que repetir el lote con cuidado."""


class ProcesarLoteUseCase(IProcesarLoteUseCase):
    def __init__(
        self,
        *,
        uow: IUnidadDeTrabajo,
        movimientos: IMovimientoCommandRepository,
        membresias: IMembresiaCommandRepository,
        progreso: IProgresoCommandRepository,
        aparcados: IAparcados,
        trazas: ITrazas,
        topics: dict[str, Topic],  # {"gastos.movimientos": Topic.MOVIMIENTOS, …}: los nombres son configuración
    ):
        self.uow = uow
        self.movimientos = movimientos
        self.membresias = membresias
        self.progreso = progreso
        self.aparcados = aparcados
        self.trazas = trazas
        self.topics = topics

    def ejecutar(self, entrada: ProcesarLoteInputDTO) -> int:
        """Aplica el lote. Devuelve cuántos mensajes tenía. EsquemaDesconocidoException (y cualquier error que no
        sea del mensaje, como una base de datos caída) sale de aquí sin haber confirmado nada."""
        try:
            self._aplicar(entrada.mensajes, con_cuidado=False)
        except _HayVenenososException:
            self._aplicar(entrada.mensajes, con_cuidado=True)  # la transacción anterior se deshizo entera
        return len(entrada.mensajes)

    def _aplicar(self, mensajes: list[MensajeInputDTO], *, con_cuidado: bool) -> None:
        progreso: dict[tuple[str, int], tuple[int, datetime]] = {}
        aparcados = 0
        with self.uow:
            for m in mensajes:
                with self.trazas.procesando(m) as traza:
                    if not con_cuidado:
                        try:
                            resultado = self._aplicar_uno(m)
                        except EventoInvalidoException as e:
                            raise _HayVenenososException from e  # deshace el lote y se repite con cuidado
                    else:
                        try:
                            with self.uow.savepoint():  # si este mensaje falla, se deshace solo él
                                resultado = self._aplicar_uno(m)
                        except EventoInvalidoException as e:
                            self.aparcados.aparcar(m, e.causa)
                            aparcados += 1
                            resultado = Resultado.APARCADO
                    traza.resultado(resultado)
                progreso[(m.topic, m.particion)] = (m.offset, m.marca)
            for (topic, particion), (offset, marca) in progreso.items():
                self.progreso.guardar(topic, particion, offset, marca)
            # Antes de confirmar nada: los aparcados tienen que estar a salvo. Si no, excepción → el lote se
            # repite (y quizá se aparquen dos veces: mejor eso que perder el mensaje)
            if aparcados:
                self.aparcados.confirmar()

    def _aplicar_uno(self, m: MensajeInputDTO) -> Resultado:
        evento = interpretar(self.topics.get(m.topic), m.clave, m.valor, m.cabeceras)
        match evento:
            case MovimientoGuardadoEvent(movimiento):
                return Resultado.GUARDADO if self.movimientos.guardar(movimiento) else Resultado.IGNORADO
            case MovimientoEliminadoEvent(movimiento_id, version):
                return Resultado.BORRADO if self.movimientos.eliminar(movimiento_id, version) else Resultado.IGNORADO
            case MembresiaGuardadaEvent(membresia):
                return Resultado.GUARDADO if self.membresias.guardar(membresia) else Resultado.IGNORADO
            case MembresiaEliminadaEvent(hogar_id, usuario_id, version):
                borrada = self.membresias.eliminar(hogar_id, usuario_id, version)
                return Resultado.BORRADO if borrada else Resultado.IGNORADO
            case None:
                logger.warning("Topic desconocido: %s", m.topic)
                return Resultado.IGNORADO
