# core/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models).
# Viven en infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulos 87 y 88).
# ModeloConFechas es abstracto: la base de los modelos de todas las apps, que lo importan de aquí.
from core.infrastructure.database.models.adjunto_model import Adjunto
from core.infrastructure.database.models.modelo_con_fechas_model import ModeloConFechas
from core.infrastructure.database.models.registro_auditoria_model import RegistroAuditoria

__all__ = ["Adjunto", "ModeloConFechas", "RegistroAuditoria"]
