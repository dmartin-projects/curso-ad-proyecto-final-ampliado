# backoffice/infrastructure/api/permissions/personal.py — los permisos de todas las vistas del backoffice (módulos 79, 88 y 92)
from rest_framework.permissions import IsAuthenticated

from backoffice.infrastructure.api.permissions.es_personal import EsPersonal
from backoffice.infrastructure.api.permissions.permisos_por_accion import PermisosPorAccion
from usuarios.infrastructure.api.permissions.sesion_multifactor import SesionMultifactor

# Ejercicio 1 del módulo 92: el personal, siempre con una sesión de dos factores (ve los datos de todos los hogares)
PERSONAL = [IsAuthenticated, EsPersonal, SesionMultifactor, PermisosPorAccion]
