# hogares/infrastructure/signals/receivers.py — la alarma de las membresías (módulo 88)
#
# Las membresías tienen eventos (el outbox de Kafka: quién ve qué estadísticas; los grupos del WebSocket): solo se
# escriben con los use cases de hogares. Una escritura con el ORM fuera de ellos perdería esos eventos en silencio.
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.infrastructure.signals.red_de_seguridad import vigilar
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


@receiver([post_save, post_delete], sender=MembresiaModel, dispatch_uid="hogares_vigilar_membresias")
def vigilar_escrituras(sender, instance, origin=None, raw=False, **kwargs):
    vigilar(instance, origin=origin, raw=raw)
