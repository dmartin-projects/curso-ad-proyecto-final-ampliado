# hogares/infrastructure/api/base/hogar_desde_url_mixin.py — el hogar de la URL y la membresía de quien pide (módulos 36, 88 y 90)
from functools import cached_property

from rest_framework.exceptions import NotFound

from core.domain.vo.actor import Actor
from hogares.infrastructure.api.base.actor_de import actor_de
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

    @property
    def actor(self) -> Actor:
        """Quién pide el use case (módulos 87 y 90): el usuario y su rol en ESTE hogar (la membresía ya resuelta),
        limitado por los scopes si llega con un token OAuth."""
        return actor_de(self.request, self.membresia.rol)

    def es_esquema(self) -> bool:
        """True mientras drf-spectacular genera el esquema (no hay usuario real)."""
        return getattr(self, "swagger_fake_view", False)
