# usuarios/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Vive en
# infrastructure/database/models/; este módulo es la puerta de entrada (módulos 87 y 88).
from usuarios.infrastructure.database.models.usuario_model import Usuario

__all__ = ["Usuario"]
