# informes/models.py — Django busca los modelos de cada app en <app>.models (AppConfig.import_models). Viven en
# infrastructure/database/models/, uno por archivo; este módulo es la puerta de entrada (módulos 87 y 88).
# ruta_informe también: la migración 0001 la usa como informes.models.ruta_informe.
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual, ruta_informe

__all__ = ["InformeMensual", "ruta_informe"]
