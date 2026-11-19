/**
 * Minimal typed wrapper around `fetch` for the Routine Manager API.
 *
 * The backend session lives in HttpOnly cookies, so every request is sent with
 * `credentials: 'include'`. In development Vite proxies `/api` to the FastAPI
 * server (see `vite.config.ts`), which keeps the cookies same-origin.
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

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { method = 'GET', body } = options;

  const response = await fetch(path, {
    method,
    credentials: 'include',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    throw await toApiError(response);
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
