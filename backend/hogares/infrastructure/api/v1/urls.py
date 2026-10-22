# hogares/infrastructure/api/v1/urls.py — las rutas de los hogares: la app es dueña de sus endpoints (módulos 71 y 88)
#
# El router principal (config/api_v1.py) solo monta este módulo; aquí está el router de DRF de la app.
from django.urls import path
from rest_framework.routers import DefaultRouter

from hogares.infrastructure.api.v1.views.aceptar_invitacion_view import AceptarInvitacionView
from hogares.infrastructure.api.v1.views.hogar_viewset import HogarViewSet
from hogares.infrastructure.api.v1.views.miembros_viewset import MiembrosViewSet

router = DefaultRouter()
router.register("hogares", HogarViewSet, basename="hogar")
router.register(r"hogares/(?P<hogar_pk>\d+)/miembros", MiembrosViewSet, basename="hogar-miembros")

urlpatterns = router.urls + [
    path("invitaciones/<str:token>/aceptar/", AceptarInvitacionView.as_view(), name="invitacion-aceptar"),
]
