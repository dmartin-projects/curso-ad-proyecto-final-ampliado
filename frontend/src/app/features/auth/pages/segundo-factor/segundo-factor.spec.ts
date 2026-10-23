import { HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { Passkeys } from '../../../../core/auth/passkeys';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import SegundoFactor from './segundo-factor';

/** Módulo 92: el segundo paso del login. */
describe('Segundo factor', () => {
  let ctrl: HttpTestingController;
  let navegar: ReturnType<typeof vi.spyOn>;
  let firmar: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    firmar = vi.fn().mockResolvedValue({ id: 'cred', type: 'public-key' });
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Passkeys, useValue: { disponible: () => true, firmar } },
      ],
    });
    ctrl = TestBed.inject(HttpTestingController);
    navegar = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
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

  async function pintar(factores: string[], volver?: string) {
    const fixture = TestBed.createComponent(SegundoFactor);
    if (volver) fixture.componentRef.setInput('volver', volver);
    (await peticion('/api/v1/auth/mfa/')).flush({ factores });
    await fixture.whenStable();
    return fixture;
  }

  const boton = (f: ComponentFixture<SegundoFactor>, texto: string) =>
    [...(f.nativeElement as HTMLElement).querySelectorAll('button')].find((b) =>
      b.textContent?.includes(texto),
    );

  async function escribirYEnviar(f: ComponentFixture<SegundoFactor>, codigo: string) {
    const input = (f.nativeElement as HTMLElement).querySelector('input')!;
    input.value = codigo;
    input.dispatchEvent(new Event('input'));
    boton(f, 'Verificar')!.click();
  }

  it('con el código de la app entra y vuelve adonde iba', async () => {
    const f = await pintar(['totp', 'recuperacion'], '/hogares/3');
    await escribirYEnviar(f, '123456');
    const enviado = await peticion('/api/v1/auth/mfa/', 'POST');
    expect(enviado.request.body).toEqual({ factor: 'totp', codigo: '123456' });
    enviado.flush({ access: 'token' });
    (await peticion('/api/v1/auth/me/')).flush({
      id: 1,
      email: 'ana@example.com',
      es_personal: false,
    });
    await vi.waitFor(() => expect(navegar).toHaveBeenCalledWith('/hogares/3'));
  });

  it('con un código de recuperación', async () => {
    const f = await pintar(['totp', 'recuperacion']);
    boton(f, 'código de recuperación')!.click();
    await f.whenStable();
    await escribirYEnviar(f, 'ABCD-EFGH-JKMN-PQRS');
    const enviado = await peticion('/api/v1/auth/mfa/', 'POST');
    expect(enviado.request.body).toEqual({ factor: 'recuperacion', codigo: 'ABCD-EFGH-JKMN-PQRS' });
    enviado.flush({ access: 'token' });
    (await peticion('/api/v1/auth/me/')).flush({
      id: 1,
      email: 'ana@example.com',
      es_personal: false,
    });
  });

  it('con una passkey: el reto de SU cuenta, firmado', async () => {
    const f = await pintar(['totp', 'passkey', 'recuperacion']);
    boton(f, 'Usar una passkey')!.click();
    (await peticion('/api/v1/auth/mfa/reto/', 'POST')).flush({
      challenge: 'reto',
      allowCredentials: [],
    });
    await vi.waitFor(() =>
      expect(firmar).toHaveBeenCalledWith({ challenge: 'reto', allowCredentials: [] }),
    );
    const enviado = await peticion('/api/v1/auth/mfa/', 'POST');
    expect(enviado.request.body).toEqual({
      factor: 'passkey',
      respuesta: { id: 'cred', type: 'public-key' },
    });
    enviado.flush({ access: 'token' });
    (await peticion('/api/v1/auth/me/')).flush({
      id: 1,
      email: 'ana@example.com',
      es_personal: false,
    });
    await vi.waitFor(() => expect(navegar).toHaveBeenCalledWith('/hogares'));
  });

  it('sin el primer paso (caducado o de otro navegador), vuelta a entrar', async () => {
    const fixture = TestBed.createComponent(SegundoFactor);
    (await peticion('/api/v1/auth/mfa/')).flush(
      { type: 'login_pendiente_no_valido', title: 'El inicio de sesión ha caducado.' },
      { status: 401, statusText: 'Unauthorized' },
    );
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('El inicio de sesión ha caducado.');
  });
});
