# config/api_v1.py — el router principal de la API v1: SOLO monta, una línea por app (módulo 87)
#
# Cada app es dueña de sus endpoints (su infrastructure/api/v1/urls.py, o api/urls.py en las apps que aún no siguen
# la estructura hexagonal). Aquí no hay views ni lógica: si mañana una app se va a otro servicio, se borra su línea.
from django.urls import include, path

urlpatterns = [
    path("auth/", include("usuarios.api.urls")),
    path("", include("hogares.api.urls")),
    path("", include("finanzas.infrastructure.api.v1.urls")),
    path("", include("tickets.api.urls")),
    path("", include("importaciones.api.urls")),
    path("", include("notificaciones.api.urls")),
    path("", include("informes.api.urls")),
    path("backoffice/", include("backoffice.api.urls")),
]
