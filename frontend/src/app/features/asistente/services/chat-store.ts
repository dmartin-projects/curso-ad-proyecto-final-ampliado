import { inject } from '@angular/core';
import { patchState, signalStore, withHooks, withMethods, withState } from '@ngrx/signals';
import { QueryClient } from '@tanstack/angular-query-experimental';
import { firstValueFrom, Subscription } from 'rxjs';

import { ErrorApi } from '../../../core/http/errores';
import {
  ConversacionDetalle,
  DatosDelMensaje,
  EventoChat,
  GraficoDelChat,
  MensajeChat,
  Pregunta,
  PropuestaDelChat,
} from '../interfaces/asistente.models';
import { AsistenteApi } from './asistente-api';
import { clavesAsistente } from './consultas';

interface EstadoChat {
  hogarId: number | null;
  conversacionId: number | null;
  titulo: string;
  mensajes: MensajeChat[];
  enCurso: boolean; // hay una respuesta llegando
  pasos: string[]; // "Mirando el resumen del mes", mientras responde
  borrador: string; // el texto de la respuesta, según llega
  datos: DatosDelMensaje; // gráficos, archivos y propuestas que ya han llegado
  error: string | null;
}

const VACIO: Omit<EstadoChat, 'hogarId'> = {
  conversacionId: null,
  titulo: '',
  mensajes: [],
  enCurso: false,
  pasos: [],
  borrador: '',
  datos: {},
  error: null,
};

/** Los datos del evento, sin el nombre del evento. */
function sinEvento<T extends { evento: string }>(ev: T): Omit<T, 'evento'> {
  const datos: Partial<T> = { ...ev };
  delete datos.evento;
  return datos as Omit<T, 'evento'>;
}

function desdeLaApi(d: ConversacionDetalle): MensajeChat[] {
  return d.mensajes.map((m) => ({
    id: m.id,
    rol: m.rol,
    texto: m.texto,
    datos: m.datos as DatosDelMensaje,
    incompleto: m.incompleto,
    nombreAdjunto: m.nombre_adjunto || undefined,
  }));
}

/**
 * Estado de CLIENTE de la conversación abierta: los mensajes y la respuesta que está llegando (módulo 97). La lista de
 * conversaciones y carpetas es estado de servidor (TanStack, en la page). Una instancia por page (providers).
 */
export const ChatStore = signalStore(
  withState<EstadoChat>({ hogarId: null, ...VACIO }),
  withMethods((store, api = inject(AsistenteApi), queryClient = inject(QueryClient)) => {
    let respuesta: Subscription | null = null;

    const invalidarLista = () =>
      queryClient.invalidateQueries({ queryKey: clavesAsistente.todo(store.hogarId()!) });

    const incompleta = (error: string | null) =>
      patchState(store, (s) => ({
        enCurso: false,
        pasos: [],
        borrador: '',
        datos: {},
        error,
        mensajes: s.mensajes.map((m, i) =>
          i === s.mensajes.length - 1 ? { ...m, incompleto: true } : m,
        ),
      }));

    const procesar = (ev: EventoChat) => {
      switch (ev.evento) {
        case 'tool': // el texto que hubiera era de un turno con tools: no es la respuesta
          return patchState(store, (s) => ({ pasos: [...s.pasos, ev.texto], borrador: '' }));
        case 'texto':
          return patchState(store, (s) => ({ borrador: s.borrador + ev.delta }));
        case 'grafico': {
          const grafico = sinEvento(ev);
          return patchState(store, (s) => ({
            datos: { ...s.datos, graficos: [...(s.datos.graficos ?? []), grafico] },
          }));
        }
        case 'archivo': {
          const archivo = sinEvento(ev);
          return patchState(store, (s) => ({
            datos: { ...s.datos, archivos: [...(s.datos.archivos ?? []), archivo] },
          }));
        }
        case 'propuesta': {
          const propuesta = sinEvento(ev);
          return patchState(store, (s) => ({
            datos: { ...s.datos, propuestas: [...(s.datos.propuestas ?? []), propuesta] },
          }));
        }
        case 'recuerdo': {
          const recuerdo = sinEvento(ev);
          return patchState(store, (s) => ({
            datos: { ...s.datos, recuerdos: [...(s.datos.recuerdos ?? []), recuerdo] },
          }));
        }
        case 'datos': {
          const consulta = sinEvento(ev);
          return patchState(store, (s) => ({
            datos: { ...s.datos, consultas: [...(s.datos.consultas ?? []), consulta] },
          }));
        }
        case 'fuentes':
          return patchState(store, (s) => ({
            datos: { ...s.datos, fuentes: [...(s.datos.fuentes ?? []), ...ev.fuentes] },
          }));
        case 'titulo':
          return patchState(store, { titulo: ev.titulo });
        case 'fin': {
          // Los artefactos, los que ya llegaron (con la URL del archivo y el estado de la propuesta)
          patchState(store, (s) => {
            const respuesta: MensajeChat = {
              id: ev.mensaje,
              rol: 'modelo',
              texto: ev.texto,
              datos: { ...s.datos, seguimiento: ev.seguimiento },
            };
            return {
              ...VACIO,
              conversacionId: s.conversacionId,
              titulo: s.titulo,
              mensajes: [...s.mensajes, respuesta],
            };
          });
          return invalidarLista();
        }
        case 'error':
          return incompleta(ev.detalle);
        default:
          return undefined;
      }
    };

    return {
      vaciar(hogarId: number) {
        respuesta?.unsubscribe();
        patchState(store, { hogarId, ...VACIO });
      },
      async abrir(hogarId: number, id: number) {
        respuesta?.unsubscribe();
        patchState(store, { hogarId, ...VACIO, conversacionId: id });
        const d = await firstValueFrom(api.leer(hogarId, id));
        patchState(store, { titulo: d.conversacion.titulo ?? '', mensajes: desdeLaApi(d) });
      },
      /** Una conversación nueva, vacía: devuelve su id (la page navega a ella). */
      async nueva(hogarId: number) {
        const d = await firstValueFrom(api.crear(hogarId));
        patchState(store, { hogarId, ...VACIO, conversacionId: d.conversacion.id });
        invalidarLista();
        return d.conversacion.id;
      },
      preguntar(pregunta: Pregunta) {
        const hogarId = store.hogarId()!;
        const conversacion = store.conversacionId()!;
        const nuevo: MensajeChat = {
          rol: 'usuario',
          texto: pregunta.texto,
          datos: {},
          nombreAdjunto: pregunta.archivo?.name,
        };
        patchState(store, (s) => ({
          mensajes: [...s.mensajes, nuevo],
          enCurso: true,
          pasos: [],
          borrador: '',
          datos: {},
          error: null,
        }));
        respuesta = api.preguntar(hogarId, conversacion, pregunta).subscribe({
          next: procesar,
          error: (e: unknown) =>
            incompleta(e instanceof ErrorApi ? e.titulo : 'No se ha podido preguntar.'),
          complete: () => store.enCurso() && incompleta('La respuesta se ha cortado.'),
        });
      },
      /** Cancelar la suscripción aborta la petición: el backend deja de pedir vueltas al modelo. */
      detener() {
        respuesta?.unsubscribe();
        respuesta = null;
        incompleta(null);
      },
      async resolver(propuesta: PropuestaDelChat, accion: 'confirmar' | 'descartar') {
        const r = await firstValueFrom(
          accion === 'confirmar'
            ? api.confirmar(store.hogarId()!, propuesta.id)
            : api.descartar(store.hogarId()!, propuesta.id),
        );
        const estado = r.estado as PropuestaDelChat['estado'];
        patchState(store, (s) => ({
          mensajes: s.mensajes.map((m) => ({
            ...m,
            datos: {
              ...m.datos,
              propuestas: m.datos.propuestas?.map((p) =>
                p.id === propuesta.id ? { ...p, estado } : p,
              ),
            },
          })),
        }));
      },
      fijar(grafico: GraficoDelChat) {
        return firstValueFrom(api.fijar(store.hogarId()!, grafico));
      },
      async renombrar(titulo: string) {
        await firstValueFrom(api.modificar(store.hogarId()!, store.conversacionId()!, { titulo }));
        patchState(store, { titulo });
        invalidarLista();
      },
    };
  }),
  // Si la persona se va de la página con una respuesta llegando, la petición se aborta: el backend deja de pagar
  withHooks((store) => ({ onDestroy: () => store.enCurso() && store.detener() })),
);
