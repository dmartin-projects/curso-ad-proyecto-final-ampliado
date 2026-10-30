# asistente/tests/fakes/emisor_de_eventos_fake.py — IEmisorDeEventos que apunta los eventos (módulo 97)
from asistente.application.ports.i_emisor_de_eventos import IEmisorDeEventos


class EmisorDeEventosFake(IEmisorDeEventos):
    """Apunta (tipo, datos). Con `cancelar_tras`, la persona "se va" después de ese evento."""

    def __init__(self, cancelar_tras: str | None = None):
        self.eventos: list[tuple[str, dict]] = []
        self.cancelar_tras = cancelar_tras
        self._cancelado = False

    def emitir(self, tipo, datos):
        self.eventos.append((tipo, datos))
        if tipo == self.cancelar_tras:
            self._cancelado = True

    def cancelado(self):
        return self._cancelado

    def tipos(self) -> list[str]:
        return [t for t, _ in self.eventos]

    def de(self, tipo: str) -> list[dict]:
        return [d for t, d in self.eventos if t == tipo]
