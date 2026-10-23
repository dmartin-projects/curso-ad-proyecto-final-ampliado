import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { SIN_AUTH } from '../http/contexto';
import { AuthStore } from './auth-store';
import { esReautenticacion } from './reautenticacion';

/** Nuestras APIs: Django y, desde el módulo 85, el servicio de estadísticas. A NINGUNA otra URL va el token. */
export const APIS_PROPIAS = ['/api/', '/estadisticas/'];
const esApiPropia = (url: string) => APIS_PROPIAS.some((prefijo) => url.startsWith(prefijo));

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (!esApiPropia(req.url) || req.context.get(SIN_AUTH)) return next(req);

  const auth = inject(AuthStore);
  const conToken = (r: HttpRequest<unknown>, token: string | null) =>
    token ? r.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : r;

  return next(conToken(req, auth.access())).pipe(
    catchError((error: unknown) => {
      // (módulo 92: el 401 del step-up no es un access caducado; si llega aquí es que la persona no ha confirmado)
      if (!(error instanceof HttpErrorResponse) || error.status !== 401 || esReautenticacion(error))
        return throwError(() => error);
      // access caducado: refrescar (una sola vez para todas las peticiones) y reintentar
      return auth.refrescar().pipe(
        switchMap((nuevo) => next(conToken(req, nuevo))),
        catchError((e) => {
          auth.logout();
          return throwError(() => e);
        }),
      );
    }),
  );
};
