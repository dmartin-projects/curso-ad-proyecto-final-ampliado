import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { Avisos } from './avisos';
import { SIN_AVISO_ERROR } from './contexto';

/** Formato de error de la API (módulo 38): {type, title, status, detail, errors, request_id}. */
interface Problema {
  type: string;
  title: string;
  detail: unknown;
  errors: Record<string, string[]> | null;
  request_id: string | null;
}

export class ErrorApi extends Error {
  constructor(
    readonly status: number,
    readonly tipo: string, // "validacion", "sin_permiso", "ticket_estado_no_permitido"…
    readonly titulo: string,
    readonly errores: Record<string, string[]> = {},
    readonly requestId?: string,
  ) {
    super(titulo);
  }
}

/** El cuerpo del error: un objeto o, en una petición de texto (el streaming del chat, módulo 97), su JSON. */
function cuerpo(error: unknown): Partial<Problema> | null {
  if (typeof error !== 'string') return error as Partial<Problema> | null;
  try {
    return JSON.parse(error) as Partial<Problema>;
  } catch {
    return null;
  }
}

export const erroresInterceptor: HttpInterceptorFn = (req, next) => {
  const avisos = inject(Avisos);
  return next(req).pipe(
    catchError((e: unknown) => {
      if (!(e instanceof HttpErrorResponse)) return throwError(() => e);
      const p = cuerpo(e.error);
      const error =
        e.status === 0
          ? new ErrorApi(0, 'sin_conexion', 'No se puede conectar con el servidor.')
          : new ErrorApi(
              e.status,
              p?.type ?? 'error',
              p?.title ?? 'Error inesperado.',
              p?.errors ?? {},
              p?.request_id ?? undefined,
            );
      if (!req.context.get(SIN_AVISO_ERROR) && [0, 403, 429, 500, 502, 503].includes(e.status)) {
        avisos.error(error.titulo);
      }
      return throwError(() => error);
    }),
  );
};
