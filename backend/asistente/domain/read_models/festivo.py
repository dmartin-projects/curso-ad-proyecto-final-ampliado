# asistente/domain/read_models/festivo.py — un día festivo oficial (módulo 95, ejercicio 1)
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Festivo:
    fecha: date
    nombre: str  # en el idioma del país ("Fiesta de la Comunidad de Madrid")
    comunidades: tuple[str, ...]  # ISO 3166-2 ("ES-MD"); vacía: en todo el país

    @property
    def nacional(self) -> bool:
        return not self.comunidades
