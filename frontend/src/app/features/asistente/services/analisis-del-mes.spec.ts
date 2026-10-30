import { HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Subject } from 'rxjs';

import { MensajeWs, TiempoReal } from '../../../core/tiempo-real/tiempo-real';
import { proveedoresDeTest } from '../../../testing/proveedores';
import { AnalisisDelMes } from '../components/analisis-del-mes/analisis-del-mes';
import { AnalisisDelMesStore } from './analisis-del-mes';

const TAREA = '0b6f2c1e-8d1a-4f7e-9c3b-2a5d6e7f8a9b';

function montar() {
  const mensajes = new Subject<MensajeWs>();
  TestBed.configureTestingModule({
    providers: [
      ...proveedoresDeTest(),
      AnalisisDelMesStore,
      { provide: TiempoReal, useValue: { eventos: () => mensajes.asObservable() } },
    ],
  });
  vi.spyOn(crypto, 'randomUUID').mockReturnValue(TAREA);
  const avisar = (datos: Record<string, unknown>) =>
    mensajes.next({ tipo: 'evento', evento: 'asistente.analisis', hogar: 3, datos });
  return {
    store: TestBed.inject(AnalisisDelMesStore),
    avisar,
    http: TestBed.inject(HttpTestingController),
  };
}

describe('AnalisisDelMesStore (módulo 105)', () => {
  it('escucha antes de pedirlo, sigue SU tarea y termina con la conversación del informe', async () => {
    const { store, avisar, http } = montar();
    const fin = store.analizar(3);
    const req = http.expectOne('/api/v1/hogares/3/asistente/analisis/');
    expect(req.request.body).toEqual({ tarea: TAREA, mes: undefined });

    avisar({ tarea: TAREA, estado: 'en_curso', paso: 'Analizando el gasto' }); // antes de la respuesta HTTP
    avisar({ tarea: 'otra', estado: 'en_curso', paso: 'De otra pestaña' });
    req.flush({ tarea: TAREA, mes: '2026-10' }, { status: 202, statusText: 'Accepted' });
    expect(store.pasos()).toEqual(['Analizando el gasto']);
    expect(store.enCurso()).toBe(true);

    avisar({ tarea: TAREA, estado: 'terminado', paso: 'Análisis listo', conversacion: 41 });
    expect(await fin).toBe(41);
    expect(store.enCurso()).toBe(false);
  });

  it('si falla el trabajo o la petición, lo dice y se puede volver a pedir', async () => {
    const { store, avisar, http } = montar();
    const fin = store.analizar(3);
    http
      .expectOne(() => true)
      .flush({ tarea: TAREA, mes: '2026-10' }, { status: 202, statusText: 'Accepted' });
    avisar({
      tarea: TAREA,
      estado: 'fallido',
      paso: 'El asistente no está disponible ahora mismo.',
    });
    expect(await fin).toBeNull();
    expect(store.enCurso()).toBe(false);
    expect(store.error()).toBe('El asistente no está disponible ahora mismo.');

    const otra = store.analizar(3);
    http
      .expectOne(() => true)
      .flush(
        { detail: 'Has llegado al límite de preguntas de hoy.' },
        { status: 429, statusText: 'Too Many' },
      );
    expect(await otra).toBeNull();
    expect(store.error()).not.toBe('');
  });
});

describe('AnalisisDelMes (módulo 105)', () => {
  it('el botón, los pasos mientras dura y el error', () => {
    TestBed.configureTestingModule({ providers: proveedoresDeTest() });
    const f = TestBed.createComponent(AnalisisDelMes);
    f.componentRef.setInput('pasos', ['Analizando el gasto']);
    f.componentRef.setInput('enCurso', true);
    f.detectChanges();
    const el = f.nativeElement as HTMLElement;
    expect(el.querySelector('button')!.disabled).toBe(true);
    expect(el.textContent).toContain('Analizando el gasto');
    f.componentRef.setInput('enCurso', false);
    f.componentRef.setInput('error', 'No se ha podido.');
    f.detectChanges();
    expect(el.querySelector('[role=alert]')!.textContent).toContain('No se ha podido.');
  });
});
