# finanzas/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models).
# Viven en infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulo 87).
# Mismo app_label, mismas tablas, mismas migraciones: Django asigna la app por el paquete (finanzas), no por el
# archivo. Desde fuera de la app (factorías de los tests, otras apps), los modelos se importan de aquí.
from finanzas.infrastructure.database.models.categoria_model import Categoria
from finanzas.infrastructure.database.models.comercio_model import Comercio
from finanzas.infrastructure.database.models.cuenta_model import Cuenta
from finanzas.infrastructure.database.models.movimiento_model import Movimiento
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto

__all__ = ["Categoria", "Comercio", "Cuenta", "Movimiento", "Presupuesto"]
