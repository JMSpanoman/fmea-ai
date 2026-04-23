/**
 * Resolves the axios/fetch API base URL.
 *
 * - Default `/api` is proxied in dev (Vite strips `/api` → FastAPI root) and in prod nginx.
 * - Absolute URLs must target the FastAPI **root** (e.g. http://localhost:8000), not .../api,
 *   because routers are mounted at `/postmarket`, `/projects`, etc. A common mistake is
 *   `VITE_API_BASE_URL=http://localhost:8000/api`, which produces 404 on `/api/postmarket/report`.
 */
export function resolveApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (raw == null || String(raw).trim() === '') {
    return '/api';
  }
  let trimmed = String(raw).trim().replace(/\/$/, '');
  if (trimmed.endsWith('/api')) {
    trimmed = trimmed.slice(0, -4);
  }
  if (trimmed === '') {
    return '/api';
  }
  if (typeof window !== 'undefined') {
    try {
      const origin = window.location.origin;
      if (trimmed === origin || trimmed === `${origin}/`) {
        return '/api';
      }
      if (trimmed.startsWith(origin + '/') && !trimmed.includes('/api')) {
        return '/api';
      }
    } catch {
      // ignore
    }
  }
  return trimmed;
}
