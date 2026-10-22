# informes/infrastructure/api/v1/urls.py — las rutas de los informes (módulos 78 y 88)
from rest_framework.routers import DefaultRouter

from informes.infrastructure.api.v1.views.informe_viewset import InformeViewSet

router = DefaultRouter()
router.register(r"hogares/(?P<hogar_pk>\d+)/informes", InformeViewSet, basename="informe")

urlpatterns = router.urls
