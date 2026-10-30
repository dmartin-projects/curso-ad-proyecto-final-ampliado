import { HttpClient, HttpEventType } from '@angular/common/http';
import { inject, Service } from '@angular/core';
import { map, mergeMap, Observable } from 'rxjs';

import { archivoDe } from '../../../core/http/archivos';

import {
  Carpeta,
  Conversacion,
  ConversacionDetalle,
  Cuota,
  EventoChat,
  GraficoDelChat,
  Pregunta,
  Propuesta,
  Recuerdo,
} from '../interfaces/asistente.models';
import { LectorSSE } from './eventos-sse';

@Service()
export class AsistenteApi {
  private readonly http = inject(HttpClient);
  private readonly base = (h: number) => `/api/v1/hogares/${h}/asistente`;

  /** Con `q` (ejercicio 2 del 97), las que lo tienen en el título o en algún mensaje. */
  conversaciones(hogarId: number, carpeta?: number | null, q = '') {
    return this.http.get<Conversacion[]>(`${this.base(hogarId)}/conversaciones/`, {
      params: { ...(carpeta ? { carpeta } : {}), ...(q.trim() ? { q: q.trim() } : {}) },
    });
  }

  crear(hogarId: number, carpeta?: number | null) {
    return this.http.post<ConversacionDetalle>(`${this.base(hogarId)}/conversaciones/`, {
      carpeta: carpeta ?? null,
    });
  }

  leer(hogarId: number, id: number) {
    return this.http.get<ConversacionDetalle>(`${this.base(hogarId)}/conversaciones/${id}/`);
  }

  modificar(hogarId: number, id: number, cambios: { titulo?: string; carpeta?: number | null }) {
    return this.http.patch<ConversacionDetalle>(
      `${this.base(hogarId)}/conversaciones/${id}/`,
      cambios,
    );
  }

  /** Ejercicio 3 del 97: por la API (con el JWT), no con un <a href>, que no lleva la cabecera Authorization. */
  markdown(hogarId: number, id: number) {
    return this.http
      .get(`${this.base(hogarId)}/conversaciones/${id}/markdown/`, {
        responseType: 'blob',
        observe: 'response',
      })
      .pipe(map((r) => archivoDe(r, `conversacion-${id}.md`)));
  }

  borrar(hogarId: number, id: number) {
    return this.http.delete<void>(`${this.base(hogarId)}/conversaciones/${id}/`);
  }

  /** Módulo 98: lo gastado hoy (por quien pide) y este mes (por el hogar), con los límites de su plan. */
  cuota(hogarId: number) {
    return this.http.get<Cuota>(`${this.base(hogarId)}/cuota/`);
  }

  /** Módulo 99: lo que el asistente recuerda de quien pide (lo guarda la tool `recordar`). */
  recuerdos(hogarId: number) {
    return this.http.get<Recuerdo[]>(`${this.base(hogarId)}/recuerdos/`);
  }

  olvidar(hogarId: number, id: number) {
    return this.http.delete<void>(`${this.base(hogarId)}/recuerdos/${id}/`);
  }

  carpetas(hogarId: number) {
    return this.http.get<Carpeta[]>(`${this.base(hogarId)}/carpetas/`);
  }

  crearCarpeta(hogarId: number, nombre: string) {
    return this.http.post<Carpeta>(`${this.base(hogarId)}/carpetas/`, { nombre });
  }

  renombrarCarpeta(hogarId: number, id: number, nombre: string) {
    return this.http.patch<Carpeta>(`${this.base(hogarId)}/carpetas/${id}/`, { nombre });
  }

  borrarCarpeta(hogarId: number, id: number) {
    return this.http.delete<void>(`${this.base(hogarId)}/carpetas/${id}/`);
  }

  confirmar(hogarId: number, propuesta: number) {
    return this.http.post<Propuesta>(
      `${this.base(hogarId)}/propuestas/${propuesta}/confirmar/`,
      null,
    );
  }

  descartar(hogarId: number, propuesta: number) {
    return this.http.post<Propuesta>(
      `${this.base(hogarId)}/propuestas/${propuesta}/descartar/`,
      null,
    );
  }

  fijar(hogarId: number, { tipo, titulo, fuente, argumentos }: GraficoDelChat) {
    return this.http.post<unknown>(`${this.base(hogarId)}/graficos-fijados/`, {
      tipo,
      titulo,
      fuente,
      argumentos,
    });
  }

  /**
   * La respuesta, en streaming (Server-Sent Events). Con HttpClient y no con EventSource (solo hace GET y no deja
   * poner la cabecera Authorization) ni con fetch a pelo (se saltaría los interceptores: el token, el refresh tras un
   * 401, los errores). Con `reportProgress` y `responseType: 'text'`, cada evento de progreso trae el texto recibido
   * hasta ahora (`partialText`): se leen los eventos nuevos. Cancelar la suscripción aborta la petición: el backend
   * lo nota y deja de pagar al modelo.
   */
  preguntar(
    hogarId: number,
    conversacion: number,
    { texto, archivo }: Pregunta,
  ): Observable<EventoChat> {
    let cuerpo: FormData | { texto: string } = { texto };
    if (archivo) {
      cuerpo = new FormData();
      cuerpo.append('texto', texto);
      cuerpo.append('archivo', archivo);
    }
    const lector = new LectorSSE();
    return this.http
      .post(`${this.base(hogarId)}/conversaciones/${conversacion}/preguntar/`, cuerpo, {
        observe: 'events',
        reportProgress: true,
        responseType: 'text',
      })
      .pipe(
        mergeMap((ev) => {
          if (ev.type === HttpEventType.DownloadProgress) return lector.leer(ev.partialText ?? '');
          if (ev.type === HttpEventType.Response) return lector.leer(ev.body ?? '');
          return [];
        }),
      );
  }
}
