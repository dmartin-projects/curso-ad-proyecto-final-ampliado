import { inject, Service, signal } from '@angular/core';
import { filter, lastValueFrom, map, Subscription } from 'rxjs';

import { ErrorApi } from '../../../core/http/errores';
import { TiempoReal } from '../../../core/tiempo-real/tiempo-real';
import { AvisoDeAnalisis } from '../interfaces/asistente.models';
import { AsistenteApi } from './asistente-api';

/**
 * El análisis del mes (módulo 105): un trabajo de un minuto que hace Celery. El id de la tarea lo genera el
 * navegador, y sus avisos se escuchan ANTES de pedirlo: así no se pierde ninguno, ni siquiera si el worker es más
 * rápido que la respuesta HTTP. Al terminar, el informe es una conversación más (`analizar` devuelve su id).
 */
@Service()
export class AnalisisDelMesStore {
  private readonly api = inject(AsistenteApi);
  private readonly tiempoReal = inject(TiempoReal);
  readonly pasos = signal<string[]>([]);
  readonly enCurso = signal(false);
  readonly error = signal('');
  private escucha?: Subscription;

  analizar(hogarId: number): Promise<number | null> {
    const tarea = crypto.randomUUID();
    this.pasos.set([]);
    this.error.set('');
    this.enCurso.set(true);
    this.escucha?.unsubscribe();
    return new Promise((resolver) => {
      this.escucha = this.tiempoReal
        .eventos('asistente.analisis')
        .pipe(
          map((m) => m.datos as unknown as AvisoDeAnalisis),
          filter((d) => d.tarea === tarea),
        )
        .subscribe((d) => {
          if (d.estado === 'en_curso') this.pasos.update((p) => [...p, d.paso]);
          else
            resolver(this.terminar(d.estado === 'fallido' ? d.paso : '', d.conversacion ?? null));
        });
      lastValueFrom(this.api.analizar(hogarId, tarea)).catch((e: unknown) =>
        resolver(
          this.terminar(
            e instanceof ErrorApi ? e.titulo : 'No se ha podido pedir el análisis.',
            null,
          ),
        ),
      );
    });
  }

  private terminar(error: string, conversacion: number | null): number | null {
    this.error.set(error);
    this.enCurso.set(false);
    this.escucha?.unsubscribe();
    return conversacion;
  }
}
