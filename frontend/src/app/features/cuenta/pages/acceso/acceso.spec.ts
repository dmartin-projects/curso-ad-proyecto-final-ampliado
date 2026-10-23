import { HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Acceso as DatosAcceso } from '../../../../core/api/tipos';
import { Navegador } from '../../../../core/auth/social';
import { Confirmaciones } from '../../../../shared/components/confirmar/confirmaciones';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import Acceso from './acceso';

const SOLO_GOOGLE: DatosAcceso = {
  contrasena: false,
  identidades: [
    {
      proveedor: 'google',
      nombre: 'Google',
      email: 'ana@gmail.com',
      desde: '2026-10-20T10:00:00Z',
      ultimo_uso: '2026-10-22T18:30:00Z',
    },
  ],
};

/** Módulo 91: «Métodos de acceso». */
describe('Métodos de acceso', () => {
  let ctrl: HttpTestingController;
  let ir: ReturnType<typeof vi.fn>;
  let confirmar: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    ir = vi.fn();
    confirmar = vi.fn();
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Navegador, useValue: { origen: () => 'https://gastos.example', ir } },
        { provide: Confirmaciones, useValue: { preguntar: confirmar } },
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
    throw new Error(`El componente no ha pedido ${metodo} ${url}`);
  }

  async function hasta(fixture: ComponentFixture<Acceso>, texto: string) {
    await vi.waitFor(async () => {
      await fixture.whenStable();
      expect(fixture.nativeElement.textContent).toContain(texto);
    });
  }

  async function pintar(datos: DatosAcceso) {
    const fixture = TestBed.createComponent(Acceso);
    (await peticion('/api/v1/auth/social/')).flush({
      origen: 'https://gastos.example',
      proveedores: [
        { id: 'google', nombre: 'Google' },
        { id: 'github', nombre: 'GitHub' },
      ],
    });
    (await peticion('/api/v1/auth/acceso/')).flush(datos);
    await hasta(fixture, 'Cuentas vinculadas');
    return fixture;
  }

  const boton = (f: ComponentFixture<Acceso>, texto: string) =>
    [...(f.nativeElement as HTMLElement).querySelectorAll('button')].find(
      (b) => b.textContent?.trim() === texto,
    )!;

  it('no deja quitar la única forma de entrar, y dice por qué', async () => {
    const fixture = await pintar(SOLO_GOOGLE);
    expect(boton(fixture, 'Desvincular').disabled).toBe(true);
    expect(fixture.nativeElement.textContent).toContain('Es tu única forma de entrar');
    expect(fixture.nativeElement.textContent).toContain('entras con Google');
  });

  it('vincular pide la ida al backend (con la sesión) y navega al proveedor', async () => {
    const fixture = await pintar(SOLO_GOOGLE);
    boton(fixture, 'Vincular').click(); // GitHub, el que falta
    const r = await peticion('/api/v1/auth/social/github/vincular/', 'POST');
    r.flush({ url: 'https://github.com/login/oauth/authorize?client_id=x&state=y' });
    await vi.waitFor(() =>
      expect(ir).toHaveBeenCalledWith(
        'https://github.com/login/oauth/authorize?client_id=x&state=y',
      ),
    );
  });

  it('establecer una contraseña enseña los motivos del servidor en el campo', async () => {
    const fixture = await pintar(SOLO_GOOGLE);
    const campo = fixture.nativeElement.querySelector('input[type=password]') as HTMLInputElement;
    campo.value = 'corta';
    campo.dispatchEvent(new Event('input'));
    boton(fixture, 'Establecer contraseña').click();
    (await peticion('/api/v1/auth/establecer-password/', 'POST')).flush(
      {
        type: 'validacion',
        title: 'Los datos enviados no son válidos.',
        status: 400,
        errors: { nueva: ['La contraseña es demasiado corta.'] },
      },
      { status: 400, statusText: 'Bad Request' },
    );
    await hasta(fixture, 'La contraseña es demasiado corta.');
  });

  it('al volver de vincular, lo dice con el nombre que da el backend', async () => {
    const fixture = TestBed.createComponent(Acceso);
    fixture.componentRef.setInput('vinculada', 'github');
    (await peticion('/api/v1/auth/social/')).flush({
      origen: 'https://gastos.example',
      proveedores: [{ id: 'github', nombre: 'GitHub' }],
    });
    (await peticion('/api/v1/auth/acceso/')).flush(SOLO_GOOGLE);
    await hasta(fixture, 'Cuenta de GitHub vinculada.');
  });

  it('con contraseña, desvincular pide confirmación y vuelve a cargar', async () => {
    const fixture = await pintar({ ...SOLO_GOOGLE, contrasena: true });
    confirmar.mockResolvedValue(true);
    boton(fixture, 'Desvincular').click();
    const r = await peticion('/api/v1/auth/acceso/google/', 'DELETE');
    r.flush(null, { status: 204, statusText: 'No Content' });
    (await peticion('/api/v1/auth/acceso/')).flush({ contrasena: true, identidades: [] });
    await vi.waitFor(async () => {
      await fixture.whenStable();
      expect(fixture.nativeElement.textContent).not.toContain('ana@gmail.com');
    });
  });
});
