import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useAuthStore, type User } from '../auth';

const USER: User = {
  id: '6f0f8f2e-8f6a-4d0e-9d3f-2b1c0a9e8d7c',
  email: 'user@example.com',
  role: 'user',
  timezone: 'UTC',
  username: 'user',
  first_name: 'Sara',
  last_name: 'Ahmadi',
  phone_number: '09120000000',
};

const REGISTRATION = {
  email: 'new@example.com',
  password: 'secret123',
  username: 'new_user',
  firstName: 'Sara',
  lastName: 'Ahmadi',
  phoneNumber: '09123456789',
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
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ identifier: USER.email, password: 'secret123' }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/v1/auth/me',
      expect.objectContaining({ method: 'GET', credentials: 'include' }),
    );
  });

  it('login() accepts a phone number as the identifier', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(200, { message: 'Logged in successfully' }))
      .mockResolvedValueOnce(jsonResponse(200, USER));

    const store = useAuthStore();
    await store.login(USER.phone_number ?? '', 'secret123');

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ identifier: USER.phone_number, password: 'secret123' }),
      }),
    );
    expect(store.user).toEqual(USER);
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

  it('login() clears a stale user when authentication fails', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(401, {
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
      }),
    );

    const store = useAuthStore();
    store.$patch({ user: USER });

    await expect(store.login(USER.email, 'wrong-password')).rejects.toMatchObject({
      code: 'INVALID_CREDENTIALS',
    });

    expect(store.user).toBeNull();
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

  it('logout() clears the user even when the API call fails', async () => {
    fetchMock.mockRejectedValueOnce(new Error('network down'));

    const store = useAuthStore();
    store.$patch({ user: USER });

    await expect(store.logout()).rejects.toThrow('network down');

    expect(store.user).toBeNull();
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

  it('updateTimezone() persists the zone and reflects it on the user', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, {
        message: 'Timezone updated successfully',
        timezone: 'Asia/Tehran',
      }),
    );

    const store = useAuthStore();
    store.$patch({ user: USER });

    await store.updateTimezone('Asia/Tehran');

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/auth/me/timezone',
      expect.objectContaining({
        method: 'PUT',
        credentials: 'include',
        body: JSON.stringify({ timezone: 'Asia/Tehran' }),
      }),
    );
    expect(store.user?.timezone).toBe('Asia/Tehran');
  });

  it('register() creates the account and signs the user in', async () => {
    fetchMock
      .mockResolvedValueOnce(
        jsonResponse(201, {
          ...USER,
          created_at: '2026-11-22T00:00:00',
        }),
      )
      .mockResolvedValueOnce(jsonResponse(200, { message: 'Logged in successfully' }))
      .mockResolvedValueOnce(jsonResponse(200, USER));

    const store = useAuthStore();
    await store.register(REGISTRATION);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/v1/auth/register',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({
          email: REGISTRATION.email,
          password: REGISTRATION.password,
          username: REGISTRATION.username,
          first_name: REGISTRATION.firstName,
          last_name: REGISTRATION.lastName,
          phone_number: REGISTRATION.phoneNumber,
        }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({
          identifier: REGISTRATION.email,
          password: REGISTRATION.password,
        }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      '/api/v1/auth/me',
      expect.objectContaining({ method: 'GET', credentials: 'include' }),
    );
    expect(store.user).toEqual(USER);
  });

  it('register() does not sign in when the email is already taken', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(400, {
        error: { code: 'EMAIL_ALREADY_EXISTS', message: 'Email is already registered.' },
      }),
    );

    const store = useAuthStore();

    await expect(store.register(REGISTRATION)).rejects.toMatchObject({
      status: 400,
      code: 'EMAIL_ALREADY_EXISTS',
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(store.user).toBeNull();
  });

  it('forgotPassword() posts the email to the mock endpoint', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { message: 'Reset link sent' }));

    const store = useAuthStore();
    await store.forgotPassword('user@example.com');

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/auth/forgot-password',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ email: 'user@example.com' }),
      }),
    );
  });

  it('forgotPassword() propagates a rejected request', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(422, {
        error: { code: 'VALIDATION_ERROR', message: 'Request validation failed.' },
      }),
    );

    const store = useAuthStore();

    await expect(store.forgotPassword('notanemail')).rejects.toMatchObject({
      status: 422,
      code: 'VALIDATION_ERROR',
    });
  });
});
