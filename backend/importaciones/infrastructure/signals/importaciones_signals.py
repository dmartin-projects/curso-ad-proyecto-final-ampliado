# importaciones/infrastructure/signals/importaciones_signals.py — el contrato con las notificaciones (módulos 76 y 88)
from django.dispatch import Signal

# Argumentos: importacion. Los escucha el módulo 76 (notificaciones y barra de progreso en tiempo real).
importacion_analizada = Signal()
importacion_progreso = Signal()
importacion_terminada = Signal()
