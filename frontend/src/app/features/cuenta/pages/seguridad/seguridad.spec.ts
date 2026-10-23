import { HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Seguridad as DatosSeguridad } from '../../../../core/api/tipos';
import { Passkeys } from '../../../../core/auth/passkeys';
import { Navegador } from '../../../../core/auth/social';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import Seguridad from './seguridad';

const SIN_NADA: DatosSeguridad = { mfa: false, codigos_restantes: 0, passkeys: [] };

/** Módulo 92: activar la verificación en dos pasos y añadir una passkey. */
describe('Seguridad', () => {
  let ctrl: HttpTestingController;
  let crear: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    crear = vi.fn().mockResolvedValue({ id: 'cred', type: 'public-key' });
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Navegador, useValue: { origen: () => 'https://gastos.example', ir: vi.fn() } },
        { provide: Passkeys, useValue: { disponible: () => true, crear } },
      ],
    });
    ctrl = TestBed.inject(HttpTestingController);
  });

  afterEach(() => ctrl.verify());

  const vuelta = () => new Promise((r) => setTimeout(r));

  async function peticion(url: string, metodo = 'GET') {
    for (let i = 0; i < 50; i++) {
      const [r] = ctrl.match((p) => p.url === url && p.method === metodo);
      if (r) return r;
      await vuelta();
    }
    throw new Error(`No ha pedido ${metodo} ${url}`);
  }

  async function hasta(fixture: ComponentFixture<Seguridad>, texto: string) {
    await vi.waitFor(async () => {
      await fixture.whenStable();
      expect(fixture.nativeElement.textContent).toContain(texto);
    });
  }

  async function pintar(datos: DatosSeguridad) {
    const fixture = TestBed.createComponent(Seguridad);
    (await peticion('/api/v1/auth/social/')).flush({
      origen: 'https://gastos.example',
      proveedores: [],
    });
    (await peticion('/api/v1/auth/seguridad/')).flush(datos);
    await hasta(fixture, datos.mfa ? 'Desactivar' : 'Además de tu contraseña'); // (con los datos ya pintados)
    return fixture;
  }

  const boton = (f: ComponentFixture<Seguridad>, texto: string) =>
    [...(f.nativeElement as HTMLElement).querySelectorAll('button')].find(
      (b) => b.textContent?.trim() === texto,
    )!;

  it('activar: el QR y la clave, el primer código y los códigos de recuperación una vez', async () => {
    const f = await pintar(SIN_NADA);
    boton(f, 'Activar').click();
    (await peticion('/api/v1/auth/seguridad/totp/', 'POST')).flush({
      secreto: 'JBSWY3DPEHPK3PXP',
      uri: 'otpauth://totp/Gastos:ana?secret=JBSWY3DPEHPK3PXP',
      qr: 'data:image/svg+xml;base64,PHN2Zy8+',
    });
    await hasta(f, 'JBSWY3DPEHPK3PXP');
    const pagina = f.nativeElement as HTMLElement;
    expect(pagina.querySelector('img')?.getAttribute('src')).toBe(
      'data:image/svg+xml;base64,PHN2Zy8+',
    );
    const input = pagina.querySelector('input')!;
    input.value = '123456';
    input.dispatchEvent(new Event('input'));
    boton(f, 'Activar').click();
    const confirmar = await peticion('/api/v1/auth/seguridad/totp/confirmar/', 'POST');
    expect(confirmar.request.body).toEqual({ codigo: '123456' });
    confirmar.flush({ codigos: ['AAAA-BBBB-CCCC-DDDD', 'EEEE-FFFF-GGGG-HHHH'] });
    (await peticion('/api/v1/auth/seguridad/')).flush({
      ...SIN_NADA,
      mfa: true,
      codigos_restantes: 2,
    });
    await hasta(f, 'AAAA-BBBB-CCCC-DDDD');
    boton(f, 'Ya los he guardado').click();
    await hasta(f, 'Te quedan 2 códigos de recuperación.');
    expect(pagina.textContent).not.toContain('AAAA-BBBB-CCCC-DDDD'); // no se vuelven a enseñar
  });

  it('añadir una passkey: el reto del backend, el autenticador y la respuesta', async () => {
    const f = await pintar(SIN_NADA);
    boton(f, 'Añadir una passkey').click();
    (await peticion('/api/v1/auth/seguridad/passkeys/reto/', 'POST')).flush({ challenge: 'reto' });
    await vi.waitFor(() => expect(crear).toHaveBeenCalledWith({ challenge: 'reto' }));
    const alta = await peticion('/api/v1/auth/seguridad/passkeys/', 'POST');
    expect(alta.request.body).toEqual({ respuesta: { id: 'cred', type: 'public-key' } });
    alta.flush({ id: 1 }, { status: 201, statusText: 'Created' });
    (await peticion('/api/v1/auth/seguridad/')).flush(SIN_NADA);
  });
});
