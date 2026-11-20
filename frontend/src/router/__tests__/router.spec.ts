import { describe, expect, it, vi } from 'vitest';
import router from '../index';

const { authStore } = vi.hoisted(() => ({
  authStore: {
    user: null as {
      id: string;
      email: string;
      role: string;
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
});
