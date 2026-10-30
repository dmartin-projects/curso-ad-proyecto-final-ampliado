export const clavesAsistente = {
  conversaciones: (hogarId: number, carpeta: number | null, q = '') =>
    ['hogar', hogarId, 'asistente', 'conversaciones', carpeta ?? 'todas', q] as const,
  carpetas: (hogarId: number) => ['hogar', hogarId, 'asistente', 'carpetas'] as const,
  todo: (hogarId: number) => ['hogar', hogarId, 'asistente'] as const,
};
