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
});
