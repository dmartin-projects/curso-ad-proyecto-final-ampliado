# eventos/infrastructure/messaging/sin_transaccion_exception.py (módulos 85 y 88)
class SinTransaccionException(RuntimeError):
    """Se ha intentado guardar un evento fuera de transaction.atomic()."""
