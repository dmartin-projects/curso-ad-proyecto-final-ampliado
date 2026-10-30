import { datosDeGrafico } from './datos-de-grafico';

describe('datosDeGrafico', () => {
  it('de lo que calcula el backend a Chart.js', () => {
    const { tipo, datos, opciones } = datosDeGrafico({
      tipo: 'lineas',
      titulo: 'Últimos meses',
      etiquetas: ['2026-09', '2026-10'],
      series: [
        { nombre: 'Gastos', valores: [776.59, 505.14] },
        { nombre: 'Ingresos', valores: [2100, 2100] },
      ],
      unidad: '€',
    });
    expect(tipo).toBe('line');
    expect(datos.labels).toEqual(['2026-09', '2026-10']);
    expect(datos.datasets.map((d) => d.label)).toEqual(['Gastos', 'Ingresos']);
    expect(opciones.plugins?.legend?.display).toBe(true);
  });
});
