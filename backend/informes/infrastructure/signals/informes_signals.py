# informes/infrastructure/signals/informes_signals.py — el contrato con las notificaciones (módulos 78 y 88)
from django.dispatch import Signal

# Argumentos: informe, enviar (bool: si hay que mandarlo por email). Lo escuchan las notificaciones.
informe_generado = Signal()
