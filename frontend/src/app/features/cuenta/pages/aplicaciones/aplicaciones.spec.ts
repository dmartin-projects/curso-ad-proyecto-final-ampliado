import { HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AplicacionConectada } from '../../../../core/api/tipos';
import { Confirmaciones } from '../../../../shared/components/confirmar/confirmaciones';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import Aplicaciones from './aplicaciones';

const CLI: AplicacionConectada = {
  client_id: 'gastos-cli',
  nombre: 'Gastos CLI',
  scopes: ['gastos:leer', 'openid'],
  desde: '2026-10-20T10:00:00Z',
  ultimo_uso: '2026-10-22T18:30:00Z',
};

describe('Aplicaciones conectadas', () => {
  let ctrl: HttpTestingController;
  let confirmar: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    confirmar = vi.fn();
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Confirmaciones, useValue: { preguntar: confirmar } },
      ],
    });
    ctrl = TestBed.inject(HttpTestingController);
  });

  afterEach(() => ctrl.verify());

  /** Una vuelta del event loop: lo que el componente hace tras un await (el diálogo, la mutation de TanStack). */
  const vuelta = () => new Promise((r) => setTimeout(r));

  /** La petición `url`, en cuanto el componente la haga (tras sus await: el diálogo, la mutation, la recarga). */
  async function peticion(url: string) {
    for (let i = 0; i < 50; i++) {
      const [r] = ctrl.match(url);
      if (r) return r;
      await vuelta();
    }
    throw new Error(`El componente no ha pedido ${url}`);
  }

  /** TanStack Query avisa del resultado fuera de la change detection de Angular: se espera a verlo pintado. */
  async function hasta(fixture: ComponentFixture<Aplicaciones>, texto: string) {
    await vi.waitFor(async () => {
      await fixture.whenStable();
      expect(fixture.nativeElement.textContent).toContain(texto);
    });
  }

  async function pintar() {
    const fixture = TestBed.createComponent(Aplicaciones);
    (await peticion('/api/v1/auth/aplicaciones/')).flush([CLI]);
    await hasta(fixture, 'Gastos CLI');
    return fixture;
  }

  it('enseña cada aplicación con lo que puede hacer, en palabras de la persona', async () => {
    const texto = (await pintar()).nativeElement.textContent;
    expect(texto).toContain('Gastos CLI');
    expect(texto).toContain('Ver los movimientos, las cuentas y el resumen de tus hogares');
    expect(texto).toContain('Saber quién eres');
  });

  it('retirar el acceso pide confirmación, llama a la API y vuelve a cargar la lista', async () => {
    const fixture = await pintar();
    confirmar.mockResolvedValue(true);
    fixture.nativeElement.querySelector('button').click();
    const borrado = await peticion('/api/v1/auth/aplicaciones/gastos-cli/');
    expect(confirmar).toHaveBeenCalledOnce();
    expect(borrado.request.method).toBe('DELETE');
    borrado.flush(null, { status: 204, statusText: 'No Content' });
    (await peticion('/api/v1/auth/aplicaciones/')).flush([]); // la lista, otra vez (invalidateQueries)
    await hasta(fixture, 'Ninguna aplicación tiene acceso a tu cuenta.');
  });

  it('si no lo confirma, no se toca nada', async () => {
    const fixture = await pintar();
    confirmar.mockResolvedValue(false);
    fixture.nativeElement.querySelector('button').click();
    await vuelta();
    expect(confirmar).toHaveBeenCalledOnce();
    ctrl.expectNone('/api/v1/auth/aplicaciones/gastos-cli/');
  });
});
