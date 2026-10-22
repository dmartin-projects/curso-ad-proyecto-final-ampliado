# hogares/infrastructure/signals/hogares_signals.py — el contrato de los hogares con las demás apps (módulos 72, 76 y 88)
from django.dispatch import Signal

# Argumentos: hogar_id. Se envía DENTRO de la transacción que crea el hogar: finanzas crea sus categorías por
# defecto en ella (módulo 72). Solo el id: quien escucha no recibe modelos de otra app.
hogar_creado = Signal()

# Argumentos: usuario_id. Al confirmarse un alta o una baja: el WebSocket de esa persona cambia de grupos (módulo 76).
miembros_cambiados = Signal()
