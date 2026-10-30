# asistente/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulo 97).
from asistente.infrastructure.database.models.carpeta_model import Carpeta
from asistente.infrastructure.database.models.conversacion_model import Conversacion
from asistente.infrastructure.database.models.grafico_fijado_model import GraficoFijado
from asistente.infrastructure.database.models.mensaje_model import Mensaje
from asistente.infrastructure.database.models.propuesta_model import Propuesta

__all__ = ["Carpeta", "Conversacion", "GraficoFijado", "Mensaje", "Propuesta"]
