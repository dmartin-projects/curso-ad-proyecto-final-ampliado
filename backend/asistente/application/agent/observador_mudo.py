# asistente/application/agent/observador_mudo.py — el observador por defecto: no hace nada (módulo 94)
from asistente.application.ports.i_observador_agente import IObservadorAgente


class ObservadorMudo(IObservadorAgente):
    """Null object: el bucle siempre tiene a quién avisar, sin `if observador:` en cada paso."""

    def respuesta(self, respuesta):
        pass

    def llamada(self, llamada):
        pass

    def resultado(self, resultado, duracion_ms):
        pass
