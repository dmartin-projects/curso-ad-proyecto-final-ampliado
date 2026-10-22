# hogares/infrastructure/api/base/hogar_desde_url_mixin.py — el hogar de la URL y la membresía de quien pide (módulos 36 y 88)
from functools import cached_property

from rest_framework.exceptions import NotFound

from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


class HogarDesdeUrlMixin:
    """Vistas anidadas en /hogares/<hogar_pk>/…

    Resuelve el hogar de la URL y la membresía del usuario. Si el usuario no pertenece
    al hogar, responde 404 (ni siquiera revela que el hogar existe).
    """

    hogar_url_kwarg = "hogar_pk"

    @cached_property
    def membresia(self) -> MembresiaModel:
        m = (
            MembresiaModel.objects.select_related("hogar")
            .filter(hogar_id=self.kwargs[self.hogar_url_kwarg], usuario=self.request.user)
            .first()
        )
        if m is None:
            raise NotFound()
        return m

    @property
    def hogar(self):
        return self.membresia.hogar

    def es_esquema(self) -> bool:
        """True mientras drf-spectacular genera el esquema (no hay usuario real)."""
        return getattr(self, "swagger_fake_view", False)
