# importaciones/infrastructure/api/v1/urls.py — las rutas de las importaciones: la app es dueña de sus endpoints (módulos 75 y 88)
from rest_framework.routers import DefaultRouter

from importaciones.infrastructure.api.v1.views.importacion_viewset import ImportacionViewSet

router = DefaultRouter()
router.register(r"hogares/(?P<hogar_pk>\d+)/importaciones", ImportacionViewSet, basename="importacion")

urlpatterns = router.urls
