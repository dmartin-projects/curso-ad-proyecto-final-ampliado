export const clavesAsistente = {
  conversaciones: (hogarId: number, carpeta: number | null, q = '') =>
    ['hogar', hogarId, 'asistente', 'conversaciones', carpeta ?? 'todas', q] as const,
  carpetas: (hogarId: number) => ['hogar', hogarId, 'asistente', 'carpetas'] as const,
  cuota: (hogarId: number) => ['hogar', hogarId, 'asistente', 'cuota'] as const, // dentro de todo(): tras cada respuesta
  todo: (hogarId: number) => ['hogar', hogarId, 'asistente'] as const,
};
