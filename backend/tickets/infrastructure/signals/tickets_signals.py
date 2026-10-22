# tickets/infrastructure/signals/tickets_signals.py — el contrato de los tickets con las demás apps (módulos 74, 76 y 88)
from django.dispatch import Signal

# Se emite al terminar el pipeline (con éxito, para revisar o con error).
# Argumentos: ticket. El módulo 76 lo conecta con las notificaciones en tiempo real.
ticket_terminado = Signal()
