# asistente/domain/enums/plan.py — los planes del asistente: cada uno con su cuota (módulo 98)
from enum import StrEnum


class Plan(StrEnum):
    BASICO = "basico"  # el de todos los hogares, sin hacer nada
    PLUS = "plus"  # más preguntas al día y más gasto al mes (lo asigna el personal: manage.py plan_asistente)
