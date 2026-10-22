# finanzas/infrastructure/api/v1/urls.py — las rutas de finanzas: la app es dueña de sus endpoints (módulo 87)
#
# El router principal (config/api_v1.py) solo monta este módulo; aquí está el router de DRF de la app.
from django.urls import path
from rest_framework.routers import DefaultRouter

from finanzas.infrastructure.api.v1.views.categoria_viewset import CategoriaViewSet
from finanzas.infrastructure.api.v1.views.comercio_viewset import ComercioViewSet
from finanzas.infrastructure.api.v1.views.cuenta_viewset import CuentaViewSet
from finanzas.infrastructure.api.v1.views.dashboard_view import DashboardView
from finanzas.infrastructure.api.v1.views.movimiento_viewset import MovimientoViewSet
from finanzas.infrastructure.api.v1.views.presupuesto_viewset import PresupuestoViewSet

router = DefaultRouter()
H = r"hogares/(?P<hogar_pk>\d+)"
router.register(f"{H}/cuentas", CuentaViewSet, basename="cuenta")
router.register(f"{H}/categorias", CategoriaViewSet, basename="categoria")
router.register(f"{H}/movimientos", MovimientoViewSet, basename="movimiento")
router.register(f"{H}/presupuestos", PresupuestoViewSet, basename="presupuesto")
router.register("comercios", ComercioViewSet, basename="comercio")

urlpatterns = router.urls + [
    path("hogares/<int:hogar_pk>/dashboard/", DashboardView.as_view(), name="dashboard"),
]
