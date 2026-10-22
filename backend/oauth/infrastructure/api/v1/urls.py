# oauth/infrastructure/api/v1/urls.py — /api/v1/auth/aplicaciones/ (ejercicio 1 del módulo 90)
from django.urls import path

from oauth.infrastructure.api.v1.views.aplicaciones_conectadas_view import AplicacionesConectadasView
from oauth.infrastructure.api.v1.views.retirar_acceso_view import RetirarAccesoView

urlpatterns = [
    path("", AplicacionesConectadasView.as_view(), name="aplicaciones-conectadas"),
    path("<str:client_id>/", RetirarAccesoView.as_view(), name="aplicacion-retirar"),
]
