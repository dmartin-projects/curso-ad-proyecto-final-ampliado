# backoffice/infrastructure/api/permissions/personal.py — los permisos de todas las vistas del backoffice (módulos 79 y 88)
from rest_framework.permissions import IsAuthenticated

from backoffice.infrastructure.api.permissions.es_personal import EsPersonal
from backoffice.infrastructure.api.permissions.permisos_por_accion import PermisosPorAccion

PERSONAL = [IsAuthenticated, EsPersonal, PermisosPorAccion]
