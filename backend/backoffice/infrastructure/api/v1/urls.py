# backoffice/infrastructure/api/v1/urls.py — las rutas del backoffice (módulos 79 y 88)
from django.urls import path
from rest_framework.routers import DefaultRouter

from backoffice.infrastructure.api.v1.views.auditoria_viewset import AuditoriaViewSet
from backoffice.infrastructure.api.v1.views.hogar_soporte_viewset import HogarSoporteViewSet
from backoffice.infrastructure.api.v1.views.importacion_soporte_viewset import ImportacionSoporteViewSet
from backoffice.infrastructure.api.v1.views.movimiento_soporte_viewset import MovimientoSoporteViewSet
from backoffice.infrastructure.api.v1.views.resumen_view import ResumenView
from backoffice.infrastructure.api.v1.views.tarea_programada_viewset import TareaProgramadaViewSet
from backoffice.infrastructure.api.v1.views.ticket_soporte_viewset import TicketSoporteViewSet
from backoffice.infrastructure.api.v1.views.usuario_soporte_viewset import UsuarioSoporteViewSet

router = DefaultRouter()
router.register("tickets", TicketSoporteViewSet, basename="soporte-ticket")
router.register("importaciones", ImportacionSoporteViewSet, basename="soporte-importacion")
router.register("hogares", HogarSoporteViewSet, basename="soporte-hogar")
router.register("usuarios", UsuarioSoporteViewSet, basename="soporte-usuario")
router.register("movimientos", MovimientoSoporteViewSet, basename="soporte-movimiento")
router.register("auditoria", AuditoriaViewSet, basename="soporte-auditoria")
router.register("tareas", TareaProgramadaViewSet, basename="soporte-tarea")

urlpatterns = [path("resumen/", ResumenView.as_view(), name="soporte-resumen"), *router.urls]
