/**
 * Un gráfico ya calculado por el backend (módulo 97): una etiqueta por punto y una o varias series. Lo producen el
 * chat (la tool `grafico`) y los gráficos fijados en el dashboard; lo dibuja `Grafico` (Chart.js).
 */
export interface GraficoDeDatos {
  tipo: 'barras' | 'lineas' | 'circular';
  titulo: string;
  etiquetas: string[];
  series: { nombre: string; valores: number[] }[];
  unidad: string;
}
