import { HttpClient } from '@angular/common/http';
import { inject, Service, signal } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import {
  defer,
  EMPTY,
  finalize,
  ignoreElements,
  interval,
  map,
  merge,
  Observable,
  repeat,
  retry,
  share,
  Subject,
  switchMap,
  takeUntil,
  tap,
  timer,
} from 'rxjs';
import { webSocket } from 'rxjs/webSocket';

import { Notificacion, TicketWs } from '../api/tipos';
import { AuthStore } from '../auth/auth-store';

/** Mensajes que envía el consumer de Channels (módulo 76). */
export type MensajeWs =
  | { tipo: 'conectado'; no_leidas: number }
  | { tipo: 'pong' }
  | {
      tipo: 'notificacion';
      datos: Pick<
        Notificacion,
        'id' | 'tipo' | 'titulo' | 'mensaje' | 'enlace' | 'hogar' | 'creado'
      >;
    }
  | { tipo: 'evento'; evento: string; hogar: number; datos: Record<string, unknown> };

export type EstadoConexion = 'desconectado' | 'conectando' | 'conectado';

/**
 * Dónde abrir el socket (módulo 86). En producción y staging la página está en Vercel, que no reenvía
 * WebSockets: el backend de cada entorno dice su URL pública en el ticket. Sin ella (desarrollo, E2E),
 * el mismo host que la página, que el proxy de `ng serve` lleva a Django.
 */
export function urlWebSocket(
  { ticket, url }: TicketWs,
  pagina: Pick<Location, 'protocol' | 'host'>,
) {
  const base =
    url ?? `${pagina.protocol === 'https:' ? 'wss' : 'ws'}://${pagina.host}/ws/notificaciones/`;
  return `${base}?ticket=${encodeURIComponent(ticket)}`;
}

/**
 * Una única conexión WebSocket para toda la app, solo mientras hay sesión:
 * - se autentica con un ticket de un solo uso (el JWT nunca va en la URL, módulo 76);
 * - si el servidor la cierra limpiamente (4000: cambiaron mis hogares; 4401: ticket caducado) reconecta con otro ticket;
 * - si se cae, reintenta con espera creciente (1 s, 2 s, 4 s… hasta 30 s);
 * - manda un "ping" cada 25 s para que ningún proxy la cierre por inactividad.
 */
@Service()
export class TiempoReal {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthStore);

  private readonly _estado = signal<EstadoConexion>('desconectado');
  readonly estado = this._estado.asReadonly();

  private readonly conexion$: Observable<MensajeWs> = defer(() => {
    this._estado.set('conectando');
    return this.http.post<TicketWs>('/api/v1/notificaciones/ws-ticket/', null);
  }).pipe(
    switchMap((respuesta) => {
      const cerrado = new Subject<void>();
      const socket = webSocket<MensajeWs | { accion: 'ping' }>({
        url: urlWebSocket(respuesta, location),
        openObserver: { next: () => this._estado.set('conectado') },
        closeObserver: {
          next: () => {
            this._estado.set('desconectado');
            cerrado.next();
          },
        },
      });
      // ⚠️ El latido muere con el socket (takeUntil). Si no, merge() nunca completaría — interval no
      // termina — y tras un cierre limpio del servidor (4000, 4401) repeat() no llegaría a reconectar.
      const latido = interval(25_000).pipe(
        tap(() => socket.next({ accion: 'ping' })),
        ignoreElements(),
        takeUntil(cerrado),
      );
      return merge(socket, latido) as Observable<MensajeWs>;
    }),
    repeat({ delay: () => timer(1_000) }),
    retry({
      delay: (_e, intento) => timer(Math.min(30_000, 1_000 * 2 ** (intento - 1))),
      resetOnSuccess: true,
    }),
    finalize(() => this._estado.set('desconectado')),
  );

  /** Compartido (`share`): da igual cuántos componentes se suscriban, hay un solo socket. */
  readonly mensajes$: Observable<MensajeWs> = toObservable(this.auth.autenticado).pipe(
    switchMap((conSesion) => (conSesion ? this.conexion$ : EMPTY)),
    share(),
  );

  /** Atajo: solo los eventos de un tipo. */
  eventos(nombre: string) {
    return this.mensajes$.pipe(
      map((m) => (m.tipo === 'evento' && m.evento === nombre ? m : null)),
      switchMap((m) => (m ? [m] : [])),
    );
  }
}
