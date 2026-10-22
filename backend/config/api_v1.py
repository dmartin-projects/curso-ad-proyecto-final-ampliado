# config/api_v1.py — el router principal de la API v1: SOLO monta, una línea por app (módulo 87)
#
# Cada app es dueña de sus endpoints (su infrastructure/api/v1/urls.py). Aquí no hay views ni lógica: si mañana una
# app se va a otro servicio, se borra su línea.
from django.urls import include, path

urlpatterns = [
    path("auth/aplicaciones/", include("oauth.infrastructure.api.v1.urls")),  # ejercicio 1 del módulo 90
    path("auth/", include("usuarios.infrastructure.api.v1.urls")),
    path("", include("hogares.infrastructure.api.v1.urls")),
    path("", include("finanzas.infrastructure.api.v1.urls")),
    path("", include("tickets.infrastructure.api.v1.urls")),
    path("", include("importaciones.infrastructure.api.v1.urls")),
    path("", include("notificaciones.infrastructure.api.v1.urls")),
    path("", include("informes.infrastructure.api.v1.urls")),
    path("backoffice/", include("backoffice.infrastructure.api.v1.urls")),
]
