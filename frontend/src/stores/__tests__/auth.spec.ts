import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useAuthStore } from '../auth';

const USER = {
  id: '6f0f8f2e-8f6a-4d0e-9d3f-2b1c0a9e8d7c',
  email: 'user@example.com',
  role: 'user',
  timezone: 'UTC',
};

let fetchMock: ReturnType<typeof vi.fn>;

function jsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as unknown as Response;
}

beforeEach(() => {
  setActivePinia(createPinia());
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('useAuthStore (F-023)', () => {
  it('login() authenticates and stores the returned user', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(200, { message: 'Logged in successfully' }))
      .mockResolvedValueOnce(jsonResponse(200, USER));

    const store = useAuthStore();
    await store.login(USER.email, 'secret123');

    expect(store.user).toEqual(USER);
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/v1/auth/login',
      expect.objectContaining({ method: 'POST', credentials: 'include' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/v1/auth/me',
      expect.objectContaining({ method: 'GET', credentials: 'include' }),
    );
  });

  it('login() rejects on 401 and keeps the user signed out', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(401, {
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
      }),
    );

    const store = useAuthStore();

    await expect(store.login(USER.email, 'wrong-password')).rejects.toMatchObject({
      status: 401,
      code: 'INVALID_CREDENTIALS',
    });

    expect(store.user).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('logout() revokes the session and clears the user', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { message: 'Logged out successfully' }));

    const store = useAuthStore();
    store.$patch({ user: USER });

    await store.logout();

    expect(store.user).toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/auth/logout',
      expect.objectContaining({ method: 'POST', credentials: 'include' }),
    );
  });

  it('init() hydrates the user from /me', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, USER));

    const store = useAuthStore();
    await store.init();

    expect(store.user).toEqual(USER);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/auth/me',
      expect.objectContaining({ method: 'GET', credentials: 'include' }),
    );
  });

  it('init() leaves the user null when /me returns 401', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(401, {
        error: { code: 'UNAUTHORIZED', message: 'Authentication required' },
      }),
    );

    const store = useAuthStore();
    await store.init();

    expect(store.user).toBeNull();
  });
});
