import { TestBed } from '@angular/core/testing';

import { proveedoresDeTest } from '../../../../testing/proveedores';
import { MensajeChat } from '../../interfaces/asistente.models';
import { Mensaje } from './mensaje';

describe('Mensaje (módulo 97)', () => {
  function montar(mensaje: MensajeChat, ultimo = true) {
    TestBed.configureTestingModule({ providers: proveedoresDeTest() });
    const fixture = TestBed.createComponent(Mensaje);
    fixture.componentRef.setInput('mensaje', mensaje);
    fixture.componentRef.setInput('ultimo', ultimo);
    fixture.detectChanges();
    return fixture;
  }

  it('el texto del modelo, escapado: un <img onerror> es texto, no una etiqueta', () => {
    const el: HTMLElement = montar({
      rol: 'modelo',
      texto: '**776,59 €** <img src=x onerror=alert(1)>',
      datos: {},
    }).nativeElement;
    expect(el.querySelector('strong')?.textContent).toBe('776,59 €');
    expect(el.querySelector('img')).toBeNull();
  });

  it('una propuesta pendiente con sus botones, y las preguntas de seguimiento que se pueden pulsar', () => {
    const fixture = montar({
      rol: 'modelo',
      texto: 'Preparado.',
      datos: {
        propuestas: [
          { id: 4, tipo: 'movimiento', resumen: 'Gasto de 3,50 €', estado: 'pendiente' },
        ],
        seguimiento: ['¿Y en agosto?'],
      },
    });
    const confirmadas: number[] = [];
    const seguidas: string[] = [];
    fixture.componentInstance.confirmar.subscribe((p) => confirmadas.push(p.id));
    fixture.componentInstance.seguir.subscribe((s) => seguidas.push(s));
    const el: HTMLElement = fixture.nativeElement;
    (
      Array.from(el.querySelectorAll('button')).find((b) =>
        b.textContent?.includes('Confirmar'),
      ) as HTMLButtonElement
    ).click();
    (el.querySelector('mat-chip') as HTMLElement).click();
    expect([confirmadas, seguidas]).toEqual([[4], ['¿Y en agosto?']]);
  });

  it('sin seguimiento si no es la última respuesta', () => {
    const el: HTMLElement = montar(
      { rol: 'modelo', texto: 'x', datos: { seguimiento: ['¿Y?'] } },
      false,
    ).nativeElement;
    expect(el.querySelector('mat-chip')).toBeNull();
  });

  it('las secciones de la ayuda que ha usado (ejercicio 2 del 100)', () => {
    const el: HTMLElement = montar({
      rol: 'modelo',
      texto: 'Pulsa Generar.',
      datos: {
        fuentes: [
          { fuente: 'informes#Pedir uno a mano', titulo: 'Informes mensuales en PDF' },
          { fuente: 'informes#Quién puede', titulo: 'Informes mensuales en PDF' },
        ],
      },
    }).nativeElement;
    expect(
      el.querySelector('[aria-label="Fuentes"]')?.textContent?.replace(/\s+/g, ' ').trim(),
    ).toBe(
      'menu_book Según la ayuda: Informes mensuales en PDF › Pedir uno a mano;Informes mensuales en PDF › Quién puede',
    );
  });
});
