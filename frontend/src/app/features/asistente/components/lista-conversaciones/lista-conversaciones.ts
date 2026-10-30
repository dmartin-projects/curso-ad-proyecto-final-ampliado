import { DatePipe } from '@angular/common';
import { Component, DestroyRef, inject, input, output, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged, Subject } from 'rxjs';

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
  readonly buscando = input(false);
  readonly nueva = output<void>();
  readonly filtrar = output<number | null>();
  readonly crearCarpeta = output<string>();
  readonly borrarCarpeta = output<Carpeta>();
  readonly renombrarCarpeta = output<{ carpeta: Carpeta; nombre: string }>();
  readonly buscar = output<string>();
  readonly descargar = output<Conversacion>();
  readonly mover = output<{ conversacion: Conversacion; carpeta: number | null }>();
  readonly borrar = output<Conversacion>();
  protected readonly nombreCarpeta = signal('');
  /** La carpeta que se está renombrando (ejercicio 1): el mismo campo, con su nombre. */
  protected readonly renombrando = signal<Carpeta | null>(null);
  protected readonly texto = new Subject<string>();

  constructor() {
    this.texto
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed(inject(DestroyRef)))
      .subscribe((t) => this.buscar.emit(t.trim()));
  }

  protected empezarARenombrar(c: Carpeta) {
    this.renombrando.set(c);
    this.nombreCarpeta.set(c.nombre);
  }

  protected guardarCarpeta() {
    const nombre = this.nombreCarpeta().trim();
    const carpeta = this.renombrando();
    if (carpeta && nombre && nombre !== carpeta.nombre)
      this.renombrarCarpeta.emit({ carpeta, nombre });
    else if (!carpeta && nombre) this.crearCarpeta.emit(nombre);
    this.renombrando.set(null);
    this.nombreCarpeta.set('');
  }
}
