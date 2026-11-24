import { describe, expect, it, vi } from 'vitest';
import router from '../index';
import type { UserRole } from '@/stores/auth';

const { authStore } = vi.hoisted(() => ({
  authStore: {
    user: null as {
      id: string;
      email: string;
      role: UserRole;
      timezone: string;
    } | null,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    init: vi.fn(),
  },
}));

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

describe('router guard (F-023)', () => {
  it('redirects unauthenticated visitors from /dashboard to /login', async () => {
    authStore.user = null;

    await router.push('/dashboard');

    expect(router.currentRoute.value.path).toBe('/login');
  });

  it('redirects unauthenticated visitors from /profile to /login', async () => {
    authStore.user = null;

    await router.push('/profile');

    expect(router.currentRoute.value.path).toBe('/login');
  });

  it('exposes the public /register route', async () => {
    await router.push('/register');

    expect(router.currentRoute.value.name).toBe('register');
  });

  it('exposes the public /forgot-password route', async () => {
    await router.push('/forgot-password');

    expect(router.currentRoute.value.name).toBe('forgot-password');
  });

  it('redirects guests who request /admin to /login', async () => {
    authStore.user = null;

    await router.push('/admin');

    expect(router.currentRoute.value.path).toBe('/login');
  });

  it('sends an authenticated non-admin to the access-denied page', async () => {
    authStore.user = {
      id: 'user-id',
      email: 'user@example.com',
      role: 'user',
      timezone: 'UTC',
    };

    await router.push('/admin');

    expect(router.currentRoute.value.path).toBe('/forbidden');
  });

  it('lets an admin into /admin', async () => {
    authStore.user = {
      id: 'admin-id',
      email: 'admin@example.com',
      role: 'admin',
      timezone: 'UTC',
    };

    await router.push('/admin');

    expect(router.currentRoute.value.path).toBe('/admin');
  });

  it('guards nested admin routes with the same role check', async () => {
    authStore.user = {
      id: 'user-id',
      email: 'user@example.com',
      role: 'mentor',
      timezone: 'UTC',
    };

    await router.push('/admin/users');

    expect(router.currentRoute.value.path).toBe('/forbidden');
  });
});
