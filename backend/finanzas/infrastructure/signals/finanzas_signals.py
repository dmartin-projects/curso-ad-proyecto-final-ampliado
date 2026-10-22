# finanzas/infrastructure/signals/finanzas_signals.py — los avisos internos de finanzas para el resto del monolito
# (módulos 15 y 87)
#
# Solo las definiciones. Las envía el publicador (messaging/publicador_eventos_django.py) cuando se confirma la
# transacción, y las escuchan finanzas (signals/receivers.py), notificaciones, importaciones y el backoffice.
from django.dispatch import Signal

# Argumentos: hogar_id, meses (set de date, día 1). Lo escuchan el dashboard (77), las alertas (76) y el WebSocket.
movimientos_cambiados = Signal()

# Argumentos: presupuesto (el modelo de Django, con `gastado` y su categoría). Lo escuchan las notificaciones (76).
presupuesto_superado = Signal()
