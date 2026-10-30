# asistente/infrastructure/api/v1/urls.py — las rutas del asistente: la app es dueña de sus endpoints (módulos 97 a 99)
from django.urls import path
from rest_framework.routers import DefaultRouter

from asistente.infrastructure.api.v1.views.analisis_view import AnalisisView, CancelarAnalisisView
from asistente.infrastructure.api.v1.views.carpeta_viewset import CarpetaViewSet
from asistente.infrastructure.api.v1.views.conversacion_viewset import ConversacionViewSet
from asistente.infrastructure.api.v1.views.cuota_view import CuotaView
from asistente.infrastructure.api.v1.views.estado_view import EstadoView
from asistente.infrastructure.api.v1.views.grafico_fijado_viewset import GraficoFijadoViewSet
from asistente.infrastructure.api.v1.views.mis_datos_view import MisDatosView
from asistente.infrastructure.api.v1.views.preguntar_view import PreguntarView
from asistente.infrastructure.api.v1.views.propuesta_viewset import PropuestaViewSet
from asistente.infrastructure.api.v1.views.recuerdo_viewset import RecuerdoViewSet

router = DefaultRouter()
A = r"hogares/(?P<hogar_pk>\d+)/asistente"
router.register(f"{A}/conversaciones", ConversacionViewSet, basename="asistente-conversacion")
router.register(f"{A}/carpetas", CarpetaViewSet, basename="asistente-carpeta")
router.register(f"{A}/propuestas", PropuestaViewSet, basename="asistente-propuesta")
router.register(f"{A}/graficos-fijados", GraficoFijadoViewSet, basename="asistente-grafico-fijado")
router.register(f"{A}/recuerdos", RecuerdoViewSet, basename="asistente-recuerdo")  # módulo 99

urlpatterns = [
    path(
        "hogares/<int:hogar_pk>/asistente/conversaciones/<int:pk>/preguntar/",
        PreguntarView.as_view(),
        name="asistente-preguntar",
    ),
    path("hogares/<int:hogar_pk>/asistente/cuota/", CuotaView.as_view(), name="asistente-cuota"),  # módulo 98
    path("hogares/<int:hogar_pk>/asistente/estado/", EstadoView.as_view(), name="asistente-estado"),  # módulo 107
    path(  # ejercicio 2 del 107
        "hogares/<int:hogar_pk>/asistente/mis-datos/", MisDatosView.as_view(), name="asistente-mis-datos"
    ),
    path("hogares/<int:hogar_pk>/asistente/analisis/", AnalisisView.as_view(), name="asistente-analisis"),  # 105
    path(  # ejercicio 1 del 105
        "hogares/<int:hogar_pk>/asistente/analisis/<uuid:tarea>/",
        CancelarAnalisisView.as_view(),
        name="asistente-analisis-cancelar",
    ),
    *router.urls,
]
