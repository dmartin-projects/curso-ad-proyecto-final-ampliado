import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.domain.vo.actor import Actor
from finanzas.application.apuntar_movimientos_use_case.dtos.apuntar_movimientos_input_dto import (
    ApuntarMovimientosInputDTO,
)
from finanzas.application.apuntar_movimientos_use_case.dtos.movimiento_apuntado_input_dto import (
    MovimientoApuntadoInputDTO,
)
from finanzas.application.crear_presupuesto_use_case.dtos.crear_presupuesto_input_dto import CrearPresupuestoInputDTO
from finanzas.domain.enums.origen import Origen
from finanzas.infrastructure import container as finanzas
from finanzas.models import Categoria, Comercio, Cuenta
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.infrastructure import container as hogares
from usuarios.models import Usuario

COMERCIOS = [
    ("Mercadona", "Supermercado", (-120, -8)),
    ("Lidl", "Supermercado", (-80, -5)),
    ("Repsol", "Combustible", (-70, -30)),
    ("Metro de Madrid", "Transporte público", (-20, -2)),
    ("Netflix", "Suscripciones", (-13, -13)),
    ("Farmacia Sol", "Farmacia", (-35, -4)),
    ("Bar Manolo", "Restaurantes", (-45, -6)),
    ("Zara", "Ropa", (-90, -15)),
]


class Command(BaseCommand):
    help = "Crea un usuario demo con un hogar y movimientos de ejemplo (solo desarrollo)."

    def add_arguments(self, parser):
        parser.add_argument("--movimientos", type=int, default=2000)
        parser.add_argument("--email", default="demo@example.com")

    @transaction.atomic
    def handle(self, *args, movimientos, email, **opciones):
        usuario, creado = Usuario.objects.get_or_create(email=email, defaults={"nombre": "Demo", "is_active": True})
        if creado:
            usuario.set_password("demo12345-demo")
            usuario.save()
        hogar_id = hogares.crear_hogar().ejecutar(CrearHogarInputDTO(usuario.pk, "Casa demo")).id
        cuenta = Cuenta.objects.create(hogar_id=hogar_id, nombre="Cuenta común")
        categorias = dict(Categoria.objects.filter(hogar_id=hogar_id).values_list("nombre", "id"))
        comercios = [(Comercio.objects.get_or_create(nombre=n)[0], cat, r) for n, cat, r in COMERCIOS]

        hoy = date.today()
        nuevos = []
        for _ in range(movimientos):
            comercio, cat, (minimo, maximo) = random.choice(comercios)
            nuevos.append(
                MovimientoApuntadoInputDTO(
                    fecha=hoy - timedelta(days=random.randint(0, 540)),
                    importe=Decimal(random.uniform(minimo, maximo)).quantize(Decimal("0.01")),
                    concepto=comercio.nombre.upper(),
                    comercio_id=comercio.pk,
                    categoria_id=categorias.get(cat),
                )
            )
        for mes in range(18):  # nóminas
            dia = (hoy.replace(day=1) - timedelta(days=30 * mes)).replace(day=28)
            nuevos.append(
                MovimientoApuntadoInputDTO(
                    fecha=dia, importe=Decimal("2150.00"), concepto="NOMINA", categoria_id=categorias["Nómina"]
                )
            )
        # Como cualquier otro proceso: por los use cases de finanzas (un INSERT y sus eventos para Kafka)
        actor = Actor.sistema(en_nombre_de=usuario.pk)
        finanzas.apuntar_movimientos().ejecutar(
            ApuntarMovimientosInputDTO(hogar_id, actor, cuenta.pk, Origen.MANUAL, tuple(nuevos))
        )
        finanzas.crear_presupuesto().ejecutar(
            CrearPresupuestoInputDTO(hogar_id, actor, categorias["Supermercado"], hoy.replace(day=1), Decimal("400"))
        )
        self.stdout.write(self.style.SUCCESS(f"Hogar {hogar_id} con {len(nuevos)} movimientos para {email}"))
