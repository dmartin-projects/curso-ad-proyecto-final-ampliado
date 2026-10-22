# tickets/infrastructure/api/v1/urls.py — las rutas de los tickets: la app es dueña de sus endpoints (módulos 74 y 88)
from rest_framework.routers import DefaultRouter

from tickets.infrastructure.api.v1.views.ticket_viewset import TicketViewSet

router = DefaultRouter()
router.register(r"hogares/(?P<hogar_pk>\d+)/tickets", TicketViewSet, basename="ticket")

urlpatterns = router.urls
