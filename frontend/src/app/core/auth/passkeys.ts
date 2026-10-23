import { Service } from '@angular/core';

/**
 * Módulo 92: WebAuthn con la API nativa del navegador. Gastos (py_webauthn) manda las opciones en el JSON de la
 * especificación; `PublicKeyCredential.parse…OptionsFromJSON()` las convierte (los `challenge` e `id` en base64url
 * pasan a ArrayBuffer) y `credential.toJSON()` hace el camino de vuelta. Las dos son de WebAuthn nivel 3 y Baseline
 * desde 2025: sin librerías. Este servicio envuelve `navigator` para poder sustituirlo en los tests.
 */
@Service()
export class Passkeys {
  /** ¿Sabe este navegador hacer passkeys con JSON? (en jsdom, o en uno muy antiguo, no: no se ofrecen). */
  disponible(): boolean {
    return (
      typeof PublicKeyCredential !== 'undefined' &&
      typeof PublicKeyCredential.parseRequestOptionsFromJSON === 'function'
    );
  }

  /** ¿Puede ofrecer las passkeys en el autorrelleno del campo email (conditional UI)? */
  async autorrelleno(): Promise<boolean> {
    return this.disponible() && (await PublicKeyCredential.isConditionalMediationAvailable?.());
  }

  /** navigator.credentials.create(): registra una passkey nueva en el autenticador. */
  async crear(opciones: PublicKeyCredentialCreationOptionsJSON): Promise<RegistrationResponseJSON> {
    const publicKey = PublicKeyCredential.parseCreationOptionsFromJSON(opciones);
    const credencial = (await navigator.credentials.create({ publicKey })) as PublicKeyCredential;
    return credencial.toJSON() as RegistrationResponseJSON;
  }

  /**
   * navigator.credentials.get(): firma el reto con una passkey. `condicional`: sin ventana; la promesa espera a que
   * la persona elija una passkey en el autorrelleno del email (hasta que se aborte con `signal`).
   */
  async firmar(
    opciones: PublicKeyCredentialRequestOptionsJSON,
    { condicional = false, signal }: { condicional?: boolean; signal?: AbortSignal } = {},
  ): Promise<AuthenticationResponseJSON> {
    const publicKey = PublicKeyCredential.parseRequestOptionsFromJSON(opciones);
    const credencial = (await navigator.credentials.get({
      publicKey,
      signal,
      ...(condicional ? { mediation: 'conditional' as CredentialMediationRequirement } : {}),
    })) as PublicKeyCredential;
    return credencial.toJSON() as AuthenticationResponseJSON;
  }
}

/** Lo que pasa cuando la persona cierra la ventana del navegador o no hay ninguna passkey: no es un error de Gastos. */
export function esCancelacion(error: unknown): boolean {
  return error instanceof DOMException && ['NotAllowedError', 'AbortError'].includes(error.name);
}
