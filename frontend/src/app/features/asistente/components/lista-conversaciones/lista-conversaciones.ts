import { DatePipe } from '@angular/common';
import { Component, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { RouterLink } from '@angular/router';

import { Carpeta, Conversacion } from '../../interfaces/asistente.models';

/** Las conversaciones, las más recientes arriba, y las carpetas para filtrarlas y ordenarlas. */
@Component({
  selector: 'app-lista-conversaciones',
  imports: [
    DatePipe,
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatMenuModule,
  ],
  templateUrl: './lista-conversaciones.html',
})
export class ListaConversaciones {
  readonly hogarId = input.required<number>();
  readonly conversaciones = input.required<Conversacion[]>();
  readonly carpetas = input.required<Carpeta[]>();
  readonly actual = input<number | null>(null);
  readonly carpeta = input<number | null>(null);
  readonly nueva = output<void>();
  readonly filtrar = output<number | null>();
  readonly crearCarpeta = output<string>();
  readonly borrarCarpeta = output<Carpeta>();
  readonly mover = output<{ conversacion: Conversacion; carpeta: number | null }>();
  readonly borrar = output<Conversacion>();
  protected readonly nombreCarpeta = signal('');

  protected guardarCarpeta() {
    const nombre = this.nombreCarpeta().trim();
    if (nombre) this.crearCarpeta.emit(nombre);
    this.nombreCarpeta.set('');
  }
}
