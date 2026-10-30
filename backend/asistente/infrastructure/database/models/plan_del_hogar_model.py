# asistente/infrastructure/database/models/plan_del_hogar_model.py — el plan de cada hogar (módulo 98)
from django.db import models

from hogares.models import Hogar


class PlanDelHogar(models.Model):
    """Solo los hogares con un plan distinto del básico tienen fila: sin fila, básico."""

    hogar = models.OneToOneField(Hogar, on_delete=models.CASCADE, primary_key=True, related_name="+")
    plan = models.CharField(max_length=20)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hogar_id}: {self.plan}"
