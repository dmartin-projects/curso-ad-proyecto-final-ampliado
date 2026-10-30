import { LectorSSE } from './eventos-sse';

describe('LectorSSE (módulo 97)', () => {
  it('devuelve solo los eventos completos y nuevos, y se salta los latidos', () => {
    const lector = new LectorSSE();
    let recibido =
      'event: inicio\ndata: {"conversacion":1,"pregunta":5}\n\nevent: texto\ndata: {"delta":"En sep';
    expect(lector.leer(recibido)).toEqual([{ evento: 'inicio', conversacion: 1, pregunta: 5 }]);

    recibido += 'tiembre"}\n\n: latido\n\n';
    expect(lector.leer(recibido)).toEqual([{ evento: 'texto', delta: 'En septiembre' }]);
    expect(lector.leer(recibido)).toEqual([]); // nada nuevo
  });

  it('el "tipo" de un gráfico no pisa el nombre del evento', () => {
    const [ev] = new LectorSSE().leer('event: grafico\ndata: {"tipo":"lineas","titulo":"x"}\n\n');
    expect(ev).toEqual({ evento: 'grafico', tipo: 'lineas', titulo: 'x' });
  });
});
