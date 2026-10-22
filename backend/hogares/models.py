# hogares/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models).
# Viven en infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulos 87 y 88).
# _token y _caducidad también: la migración 0001 los usa como hogares.models._token y hogares.models._caducidad
# (valores por defecto de dos campos), y una migración nunca se reescribe.
from hogares.infrastructure.database.models.hogar_model import Hogar
from hogares.infrastructure.database.models.invitacion_model import Invitacion, _caducidad, _token
from hogares.infrastructure.database.models.membresia_model import Membresia

__all__ = ["Hogar", "Invitacion", "Membresia", "_caducidad", "_token"]
