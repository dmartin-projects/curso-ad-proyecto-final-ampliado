# eventos/models.py — Django busca los modelos en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/; este módulo es la puerta de entrada (módulos 87 y 88).
from eventos.infrastructure.database.models.evento_pendiente_model import EventoPendiente

__all__ = ["EventoPendiente"]
