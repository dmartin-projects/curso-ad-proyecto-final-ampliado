import type { ChartData, ChartOptions, ChartType } from 'chart.js';

import { GraficoDeDatos } from '../interfaces/grafico-de-datos';

const TIPOS: Record<GraficoDeDatos['tipo'], ChartType> = {
  barras: 'bar',
  lineas: 'line',
  circular: 'doughnut',
};

/** De lo que calcula el backend a lo que pide Chart.js: el tipo, los datos y el formato de los importes. */
export function datosDeGrafico(g: GraficoDeDatos, locale = 'es') {
  const importe = new Intl.NumberFormat(locale, { style: 'currency', currency: 'EUR' });
  const opciones: ChartOptions = {
    plugins: {
      legend: { display: g.series.length > 1 || g.tipo === 'circular' },
      tooltip: {
        callbacks: { label: (c) => `${c.dataset.label}: ${importe.format(Number(c.raw))}` },
      },
    },
  };
  const datos: ChartData = {
    labels: g.etiquetas,
    datasets: g.series.map((s) => ({ label: s.nombre, data: s.valores, tension: 0.2 })),
  };
  return { tipo: TIPOS[g.tipo], datos, opciones };
}
