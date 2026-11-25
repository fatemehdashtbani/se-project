/**
 * Minimal typed wrapper around `fetch` for the Routine Manager API.
 *
 * The backend session lives in HttpOnly cookies, so every request is sent with
 * `credentials: 'include'`. In development Vite proxies `/api` to the FastAPI
 * server (see `vite.config.ts`), which keeps the cookies same-origin.
 *
 * The access-token cookie is short-lived (15 minutes by default). When it has
 * expired the request is retried once after `POST /auth/refresh`, which rotates
 * the refresh token; without this a remembered session would silently end and
 * the visitor would be sent back to the login form.
 */

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
}

interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
  };
}

const FALLBACK_MESSAGE = 'درخواست ناموفق بود. دوباره تلاش کنید.';

const REFRESH_PATH = '/api/v1/auth/refresh';

/** Login is the one endpoint where a 401 must reach the form, not a refresh. */
const NO_REFRESH_PATHS = new Set(['/api/v1/auth/login']);

/** Error codes that mean "the session needs a new access token". */
const REFRESHABLE_CODES = new Set(['TOKEN_EXPIRED', 'INVALID_TOKEN', 'UNAUTHORIZED']);

/** An error response mapped onto the backend's `{ error: { code, message } }` envelope. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

/** Shared refresh so parallel 401s rotate the token once, not once per request. */
let refreshInFlight: Promise<boolean> | null = null;

function refreshSession(): Promise<boolean> {
  if (refreshInFlight === null) {
    refreshInFlight = (async () => {
      try {
        const response = await fetch(REFRESH_PATH, {
          method: 'POST',
          credentials: 'include',
        });
        return response.ok;
      } catch {
        return false;
      } finally {
        refreshInFlight = null;
      }
    })();
  }

  return refreshInFlight;
}

export function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  return send<T>(path, options, false);
}

async function send<T>(
  path: string,
  options: ApiRequestOptions,
  retried: boolean,
): Promise<T> {
  const { method = 'GET', body } = options;

  const response = await fetch(path, {
    method,
    credentials: 'include',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await toApiError(response);

    if (
      !retried &&
      error.status === 401 &&
      REFRESHABLE_CODES.has(error.code) &&
      !NO_REFRESH_PATHS.has(path) &&
      (await refreshSession())
    ) {
      return send<T>(path, options, true);
    }

    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function toApiError(response: Response): Promise<ApiError> {
  let code = 'HTTP_ERROR';
  let message = FALLBACK_MESSAGE;

  try {
    const payload = (await response.json()) as ApiErrorPayload;
    if (payload.error?.code) {
      code = payload.error.code;
    }
    if (payload.error?.message) {
      message = payload.error.message;
    }
  } catch {
    // Non-JSON error body: keep the fallback code and message.
  }

  return new ApiError(response.status, code, message);
}
