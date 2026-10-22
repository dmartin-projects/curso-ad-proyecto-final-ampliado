# core/infrastructure/database/models/modelo_con_fechas_model.py (módulos 15, 17 y 88)
from django.db import models


class ModeloConFechas(models.Model):
    """Base abstracta: fechas de creación y actualización en todos los modelos."""

    creado = models.DateTimeField(auto_now_add=True, db_index=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
