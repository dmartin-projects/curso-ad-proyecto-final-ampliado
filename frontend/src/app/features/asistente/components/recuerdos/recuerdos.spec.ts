import { TestBed } from '@angular/core/testing';

import { proveedoresDeTest } from '../../../../testing/proveedores';
import { Recuerdo } from '../../interfaces/asistente.models';
import { Recuerdos } from './recuerdos';

describe('Recuerdos (módulo 99)', () => {
  it('lista lo que recuerda y avisa al olvidar uno', () => {
    TestBed.configureTestingModule({ providers: proveedoresDeTest() });
    const f = TestBed.createComponent(Recuerdos);
    const r: Recuerdo = {
      id: 4,
      texto: 'La cuenta común es la de ING.',
      creado: '2026-10-30T10:00:00Z',
    };
    f.componentRef.setInput('recuerdos', [r]);
    const olvidados: Recuerdo[] = [];
    f.componentInstance.olvidar.subscribe((x) => olvidados.push(x));
    f.detectChanges();
    const el = f.nativeElement as HTMLElement;
    expect(el.textContent).toContain('Lo que recuerda el asistente (1)');
    (el.querySelector('button[aria-label^="Olvidar"]') as HTMLButtonElement).click();
    expect(olvidados).toEqual([r]);
  });
});
