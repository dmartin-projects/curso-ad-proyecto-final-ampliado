import { Component, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { Pregunta } from '../../interfaces/asistente.models';

/** Escribir la pregunta (Intro envía; Mayús+Intro, salto de línea), adjuntar una foto o un PDF, enviar o detener. */
@Component({
  selector: 'app-entrada',
  imports: [FormsModule, MatButtonModule, MatFormFieldModule, MatIconModule, MatInputModule],
  templateUrl: './entrada.html',
})
export class Entrada {
  readonly ocupado = input(false);
  readonly enviar = output<Pregunta>();
  readonly detener = output<void>();
  protected readonly texto = signal('');
  protected readonly archivo = signal<File | null>(null);

  protected elegir(evento: Event) {
    const campo = evento.target as HTMLInputElement;
    this.archivo.set(campo.files?.[0] ?? null);
    campo.value = ''; // el mismo archivo, otra vez, también dispara "change"
  }

  protected teclas(evento: KeyboardEvent) {
    if (evento.key === 'Enter' && !evento.shiftKey) {
      evento.preventDefault();
      this.mandar();
    }
  }

  protected mandar() {
    const texto = this.texto().trim();
    if (!texto || this.ocupado()) return;
    this.enviar.emit({ texto, archivo: this.archivo() ?? undefined });
    this.texto.set('');
    this.archivo.set(null);
  }
}
