# oauth/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulos 87 y 90).
from oauth.infrastructure.database.models.cliente_oauth_model import ClienteOAuth

__all__ = ["ClienteOAuth"]
