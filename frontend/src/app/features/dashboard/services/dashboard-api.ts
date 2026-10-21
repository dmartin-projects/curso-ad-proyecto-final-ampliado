import { HttpClient, HttpContext, httpResource } from '@angular/common/http';
import { inject, Service, Signal } from '@angular/core';

import { Dashboard } from '../../../core/api/tipos';
import { SIN_AVISO_ERROR } from '../../../core/http/contexto';
import { DiasSemana } from '../interfaces/dashboard.models';

@Service()
export class DashboardApi {
  private readonly http = inject(HttpClient);

  /** Todo el resumen del mes (AAAA-MM) en una petición (módulo 77). */
  resumen(hogarId: number, mes: string) {
    return this.http.get<Dashboard>(`/api/v1/hogares/${hogarId}/dashboard/`, { params: { mes } });
  }

  /**
   * Del servicio de estadísticas (módulo 85), no de Django: un httpResource propio, que se vuelve a pedir solo
   * cuando cambia el hogar. Crea un resource: se llama en el contexto de inyección de quien lo usa (una page).
   */
  diasSemana(hogarId: Signal<number>) {
    return httpResource<DiasSemana>(() => ({
      url: `/estadisticas/v1/hogares/${hogarId()}/dias-semana`,
      // Sin el aviso global de error (snackbar): si el servicio cae, lo dice SU tarjeta y nadie más
      context: new HttpContext().set(SIN_AVISO_ERROR, true),
    }));
  }
}
