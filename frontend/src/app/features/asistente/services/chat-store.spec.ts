import { TestBed } from '@angular/core/testing';
import { Observable, Subject } from 'rxjs';

import { proveedoresDeTest } from '../../../testing/proveedores';
import { EventoChat } from '../interfaces/asistente.models';
import { AsistenteApi } from './asistente-api';
import { ChatStore } from './chat-store';

describe('ChatStore (módulo 97)', () => {
  /** Una API falsa: los eventos los manda el test, y apunta si se canceló la suscripción (la petición abortada). */
  function montar() {
    const eventos = new Subject<EventoChat>();
    let cancelado = false;
    const api = {
      preguntar: () =>
        new Observable<EventoChat>((suscriptor) => {
          const s = eventos.subscribe(suscriptor);
          return () => {
            s.unsubscribe();
            cancelado = true;
          };
        }),
    };
    TestBed.configureTestingModule({
      providers: [...proveedoresDeTest(), ChatStore, { provide: AsistenteApi, useValue: api }],
    });
    const chat = TestBed.inject(ChatStore);
    chat.vaciar(3);
    return { chat, eventos, cancelado: () => cancelado };
  }

  it('el texto llega a trozos, una tool lo reinicia y el fin deja la respuesta con sus artefactos', () => {
    const { chat, eventos } = montar();
    chat.preguntar({ texto: '¿Cuánto?' });
    expect(chat.enCurso()).toBe(true);
    eventos.next({ evento: 'texto', delta: 'Voy a mirar' });
    eventos.next({ evento: 'tool', nombre: 'resumen_mes', texto: 'Mirando el resumen del mes' });
    expect([chat.borrador(), chat.pasos()]).toEqual(['', ['Mirando el resumen del mes']]);
    eventos.next({ evento: 'texto', delta: 'En septiembre ' });
    eventos.next({ evento: 'texto', delta: '776,59 €.' });
    eventos.next({
      evento: 'propuesta',
      id: 4,
      tipo: 'movimiento',
      resumen: 'Gasto',
      estado: 'pendiente',
    });
    expect(chat.borrador()).toBe('En septiembre 776,59 €.');
    eventos.next({
      evento: 'fin',
      mensaje: 9,
      texto: 'En septiembre 776,59 €.',
      seguimiento: ['¿Y agosto?'],
    });

    const respuesta = chat.mensajes()[1];
    expect([chat.enCurso(), respuesta.id, respuesta.datos.seguimiento]).toEqual([
      false,
      9,
      ['¿Y agosto?'],
    ]);
    expect(respuesta.datos.propuestas).toEqual([
      { id: 4, tipo: 'movimiento', resumen: 'Gasto', estado: 'pendiente' },
    ]);
  });

  it('detener cancela la petición y la pregunta queda sin respuesta', () => {
    const { chat, cancelado } = montar();
    chat.preguntar({ texto: '¿Cuánto?' });
    chat.detener();
    expect([cancelado(), chat.enCurso(), chat.mensajes()[0].incompleto]).toEqual([
      true,
      false,
      true,
    ]);
  });

  it('un error del servidor se enseña', () => {
    const { chat, eventos } = montar();
    chat.preguntar({ texto: '¿Cuánto?' });
    eventos.next({ evento: 'error', detalle: 'El asistente no está disponible ahora mismo.' });
    expect([chat.error(), chat.enCurso()]).toEqual([
      'El asistente no está disponible ahora mismo.',
      false,
    ]);
  });
});
