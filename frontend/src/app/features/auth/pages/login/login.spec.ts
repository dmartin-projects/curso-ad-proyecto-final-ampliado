import { HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { ProveedoresSociales } from '../../../../core/api/tipos';
import { Passkeys } from '../../../../core/auth/passkeys';
import { Navegador } from '../../../../core/auth/social';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import Login from './login';

/** Los enlaces a los proveedores (el login tiene otros: «Crear cuenta», «¿Has olvidado tu contraseña?»). */
const IDAS = 'a[href^="/api/v1/auth/social/"]';

const PROVEEDORES: ProveedoresSociales = {
  origen: 'https://gastos.example',
  proveedores: [
    { id: 'google', nombre: 'Google' },
    { id: 'apple', nombre: 'Apple' },
  ],
};

/** Módulo 91: los botones de Google, GitHub y Apple en el login, y lo que dice si la vuelta trae un error. */
describe('Login con proveedores', () => {
  let ctrl: HttpTestingController;

  function pintar(origen: string, entradas: Record<string, string> = {}) {
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Navegador, useValue: { origen: () => origen, ir: vi.fn() } },
      ],
    });
    ctrl = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(Login);
    for (const [nombre, valor] of Object.entries(entradas))
      fixture.componentRef.setInput(nombre, valor);
    ctrl.expectOne('/api/v1/auth/social/').flush(PROVEEDORES);
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  afterEach(() => ctrl.verify());

  it('enlaza con la ida de cada proveedor, llevando adónde volver', () => {
    const enlaces = [
      ...pintar('https://gastos.example', { volver: '/hogares/3' }).querySelectorAll(IDAS),
    ];
    expect(enlaces.map((a) => a.textContent?.trim())).toEqual([
      'Continuar con Google',
      'Continuar con Apple',
    ]);
    expect(enlaces[0].getAttribute('href')).toBe(
      '/api/v1/auth/social/google/entrar/?volver=%2Fhogares%2F3',
    );
  });

  it('en una preview de Vercel no los ofrece: su vuelta no está registrada', () => {
    const pagina = pintar('https://gastos-git-rama-equipo.vercel.app');
    expect(pagina.querySelectorAll(IDAS)).toHaveLength(0);
    expect(pagina.textContent).toContain(
      'El acceso con Google, Apple solo está disponible en https://gastos.example',
    );
  });

  it('explica por qué no ha entrado cuando vuelve con error_social', () => {
    const pagina = pintar('https://gastos.example', {
      error_social: 'cuenta_existente',
      proveedor: 'google',
    });
    expect(pagina.querySelector('[role=alert]')?.textContent).toContain(
      'Entra con tu contraseña y vincula Google desde «Métodos de acceso»',
    );
  });
});

/** Módulo 92: con MFA, la contraseña lleva al segundo paso (no a la app). */
describe('Login con verificación en dos pasos', () => {
  it('va al segundo paso, llevando adónde volver', async () => {
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Navegador, useValue: { origen: () => 'https://gastos.example', ir: vi.fn() } },
      ],
    });
    const ctrl = TestBed.inject(HttpTestingController);
    const navegar = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    const fixture = TestBed.createComponent(Login);
    fixture.componentRef.setInput('volver', '/hogares/3');
    ctrl.expectOne('/api/v1/auth/social/').flush(PROVEEDORES);
    await fixture.whenStable();
    const pagina = fixture.nativeElement as HTMLElement;
    for (const [etiqueta, valor] of [
      ['email', 'ana@example.com'],
      ['password', 'una-clave-larga'],
    ]) {
      const input = pagina.querySelector<HTMLInputElement>(`input[type=${etiqueta}]`)!;
      input.value = valor;
      input.dispatchEvent(new Event('input'));
    }
    pagina.querySelector<HTMLButtonElement>('button[type=submit]')!.click();
    ctrl.expectOne('/api/v1/auth/login/').flush({ segundo_factor: ['totp', 'recuperacion'] });
    await vi.waitFor(() =>
      expect(navegar).toHaveBeenCalledWith(['/login/segundo-factor'], {
        queryParams: { volver: '/hogares/3' },
      }),
    );
    ctrl.verify(); // sin /auth/me/: todavía no hay sesión
  });
});

/** Módulo 92: entrar con una passkey (el botón; el autorrelleno lo prueba el E2E con el autenticador virtual). */
describe('Login con passkey', () => {
  it('pide el reto, lo firma el autenticador y entra sin contraseña', async () => {
    const firmar = vi.fn().mockResolvedValue({ id: 'cred', type: 'public-key' });
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Navegador, useValue: { origen: () => 'https://gastos.example', ir: vi.fn() } },
        {
          provide: Passkeys,
          useValue: { disponible: () => true, autorrelleno: async () => false, firmar },
        },
      ],
    });
    const ctrl = TestBed.inject(HttpTestingController);
    const navegar = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    const fixture = TestBed.createComponent(Login);
    ctrl.expectOne('/api/v1/auth/social/').flush(PROVEEDORES);
    await fixture.whenStable();
    const boton = [...(fixture.nativeElement as HTMLElement).querySelectorAll('button')].find(
      (b) => b.textContent?.trim() === 'Entrar con una passkey',
    )!;
    boton.click();
    ctrl.expectOne('/api/v1/auth/passkey/reto/').flush({ challenge: 'reto', allowCredentials: [] });
    await vi.waitFor(() =>
      expect(firmar).toHaveBeenCalledWith(
        { challenge: 'reto', allowCredentials: [] },
        { condicional: false },
      ),
    );
    const entrada = await vi.waitFor(() => ctrl.expectOne('/api/v1/auth/passkey/'));
    expect(entrada.request.body).toEqual({ respuesta: { id: 'cred', type: 'public-key' } });
    entrada.flush({ access: 'token' });
    await vi.waitFor(() =>
      ctrl.expectOne('/api/v1/auth/me/').flush({ id: 1, email: 'a@b.c', es_personal: false }),
    );
    await vi.waitFor(() => expect(navegar).toHaveBeenCalledWith('/hogares'));
    ctrl.verify();
  });
});
