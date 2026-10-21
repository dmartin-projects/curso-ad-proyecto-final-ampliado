import { HttpTestingController } from '@angular/common/http/testing';
import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { Avisos } from '../../../../core/http/avisos';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import { DiasSemana } from '../../interfaces/dashboard.models';
import { DashboardApi } from '../../services/dashboard-api';
import { DiasSemanaCard } from './dias-semana';

describe('DiasSemanaCard (servicio de estadísticas, módulo 85)', () => {
  /** Como en el dashboard: el resource lo crea DashboardApi y la tarjeta lo recibe. */
  function montar() {
    TestBed.configureTestingModule({ providers: proveedoresDeTest() });
    const datos = TestBed.runInInjectionContext(() =>
      TestBed.inject(DashboardApi).diasSemana(signal(3)),
    );
    const fixture = TestBed.createComponent(DiasSemanaCard);
    fixture.componentRef.setInput('datos', datos);
    fixture.detectChanges();
    return { fixture, ctrl: TestBed.inject(HttpTestingController) };
  }

  it('pide los datos del hogar al servicio de estadísticas', async () => {
    const { fixture, ctrl } = montar();
    const datos: DiasSemana = {
      hogar_id: 3,
      ultimo_evento: '2026-10-21T22:43:52Z',
      desde: '2026-05-01',
      hasta: '2026-10-21',
      dias: [{ dia: 1, nombre: 'lunes', gasto_medio: '115.94' }],
    };
    ctrl.expectOne('/estadisticas/v1/hogares/3/dias-semana').flush(datos);
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('servicio de estadísticas');
    ctrl.verify();
  });

  it('si el servicio está caído: la tarjeta lo dice y NO salta el aviso global', async () => {
    const { fixture, ctrl } = montar();
    const aviso = vi.spyOn(TestBed.inject(Avisos), 'error');
    ctrl
      .expectOne('/estadisticas/v1/hogares/3/dias-semana')
      .flush('Bad Gateway', { status: 502, statusText: 'Bad Gateway' }); // lo que responde Caddy
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('no están disponibles');
    expect(aviso).not.toHaveBeenCalled(); // el resto de la app sigue como si nada
  });
});
