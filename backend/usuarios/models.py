# usuarios/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/; este módulo es la puerta de entrada (módulos 87, 88 y 91).
from usuarios.infrastructure.database.models.identidad_externa_model import IdentidadExterna
from usuarios.infrastructure.database.models.usuario_model import Usuario

__all__ = ["IdentidadExterna", "Usuario"]
