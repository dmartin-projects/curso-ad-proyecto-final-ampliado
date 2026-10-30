# asistente/infrastructure/estado/estado_desde_ajustes_y_circuitos.py — IEstadoDelAsistente (módulo 107)
"""Dos cosas apagan el asistente:

- el interruptor, ASISTENTE_ACTIVO=false en el entorno: quien opera la app lo decide (un incidente de seguridad, un gasto
  que se dispara, el proveedor que cambia de condiciones). Se aplica al reiniciar los procesos, en segundos;
- todos los modelos de la cadena con el circuito abierto (módulo 94): Groq no responde. Mejor un 503 inmediato que una
  pregunta que espera 30 s a que fallen todos."""

from collections.abc import Callable

from django.conf import settings

from asistente.application.ports.i_estado_del_asistente import IEstadoDelAsistente
from asistente.domain.vo.estado_del_asistente import APAGADO, SIN_MODELOS, EstadoDelAsistente
from core.infrastructure.cache.circuit_breaker import CircuitBreaker


class EstadoDesdeAjustesYCircuitos(IEstadoDelAsistente):
    def __init__(self, circuito: Callable[[str], CircuitBreaker]):
        self.circuito = circuito  # el del container, para que el nombre del circuito sea el mismo

    def estado(self):
        if not settings.ASISTENTE_ACTIVO:
            return EstadoDelAsistente(False, APAGADO)
        modelos = [settings.ASISTENTE_MODELO, *settings.ASISTENTE_MODELOS_RESERVA]
        if all(self.circuito(m).abierto for m in modelos):
            return EstadoDelAsistente(False, SIN_MODELOS)
        return EstadoDelAsistente(True)
