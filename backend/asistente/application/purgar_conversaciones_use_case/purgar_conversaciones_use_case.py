# asistente/application/purgar_conversaciones_use_case/purgar_conversaciones_use_case.py (módulo 107)
"""La retención (RGPD, minimización y limitación del plazo): una conversación que nadie ha tocado en
ASISTENTE_RETENCION_DIAS se borra, con sus mensajes, sus propuestas y sus archivos, como si la borrara la persona. La
lanza Celery Beat cada noche; por tandas, para no tener una transacción enorme ni un worker ocupado una hora.

Lo que NO borra: el libro de cuentas (módulo 98: tokens y coste, sin contenido, lo necesita la facturación) ni los
recuerdos (módulo 99: los guarda la persona a propósito y los ve y borra en su pantalla)."""

import logging
from datetime import timedelta

from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo

logger = logging.getLogger(__name__)
TANDA = 200


class PurgarConversacionesUseCase:
    def __init__(
        self,
        *,
        conversaciones: IConversacionCommandRepository,
        almacen: IAlmacenDeArchivos,
        reloj: IReloj,
        uow: IUnidadDeTrabajo,
        dias: int,
    ):
        self.conversaciones, self.almacen, self.reloj, self.uow, self.dias = conversaciones, almacen, reloj, uow, dias

    def ejecutar(self) -> int:
        """Cuántas ha borrado."""
        antes_de = self.reloj.ahora() - timedelta(days=self.dias)
        total = 0
        while viejas := self.conversaciones.antiguas(antes_de, TANDA):
            rutas: list[str] = []
            with self.uow:
                for c in viejas:
                    rutas += self.conversaciones.archivos(c.id)
                    self.conversaciones.eliminar(c)
            for ruta in rutas:  # después del commit, como al borrar una (módulo 97)
                try:
                    self.almacen.borrar(ruta)
                except Exception:
                    logger.exception("No se pudo borrar %s", ruta)
            total += len(viejas)
        if total:
            logger.info("Retención: %s conversaciones de hace más de %s días, borradas", total, self.dias)
        return total
