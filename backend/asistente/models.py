# asistente/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulos 97 a 99).
from asistente.infrastructure.database.models.carpeta_model import Carpeta
from asistente.infrastructure.database.models.consumo_model import Consumo
from asistente.infrastructure.database.models.conversacion_model import Conversacion
from asistente.infrastructure.database.models.grafico_fijado_model import GraficoFijado
from asistente.infrastructure.database.models.mensaje_model import Mensaje
from asistente.infrastructure.database.models.plan_del_hogar_model import PlanDelHogar
from asistente.infrastructure.database.models.propuesta_model import Propuesta
from asistente.infrastructure.database.models.recuerdo_model import Recuerdo

__all__ = ["Carpeta", "Consumo", "Conversacion", "GraficoFijado", "Mensaje", "PlanDelHogar", "Propuesta", "Recuerdo"]
