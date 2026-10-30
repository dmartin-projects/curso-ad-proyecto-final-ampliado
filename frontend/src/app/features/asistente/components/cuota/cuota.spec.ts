import { TestBed } from '@angular/core/testing';

import { Cuota } from '../../interfaces/asistente.models';
import { CuotaDelAsistente } from './cuota';

function pintar(cuota: Partial<Cuota>) {
  const f = TestBed.createComponent(CuotaDelAsistente);
  f.componentRef.setInput('cuota', {
    plan: 'basico',
    tokens_hoy: 0,
    tokens_dia: 80000,
    coste_mes: '0',
    coste_mes_maximo: '0.5',
    agotada: false,
    agotada_por: '',
    renueva: '2026-10-30T00:00:00+01:00',
    ...cuota,
  } as Cuota);
  f.detectChanges();
  return (f.nativeElement as HTMLElement).textContent ?? '';
}

describe('CuotaDelAsistente (módulo 98)', () => {
  it('con menos de la mitad gastada, no molesta', () => {
    expect(pintar({ tokens_hoy: 30000 }).trim()).toBe('');
  });

  it('pasada la mitad, cuántas preguntas quedan', () => {
    expect(pintar({ tokens_hoy: 62000 })).toContain('Hoy te quedan unas 3 preguntas');
  });

  it('agotada, por qué y hasta cuándo', () => {
    expect(pintar({ agotada: true, agotada_por: 'persona', tokens_hoy: 80000 })).toContain(
      'Has llegado al límite de preguntas de hoy.',
    );
    expect(pintar({ agotada: true, agotada_por: 'hogar' })).toContain(
      'límite del asistente de este mes',
    );
  });
});
