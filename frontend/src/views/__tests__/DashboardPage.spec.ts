import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import DashboardPage from '../DashboardPage.vue';

const { authStore, logoutMock, pushMock } = vi.hoisted(() => {
  const logoutMock = vi.fn();
  return {
    logoutMock,
    pushMock: vi.fn(),
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: string;
        timezone: string;
      } | null,
      isLoading: false,
      login: vi.fn(),
      logout: logoutMock,
      init: vi.fn(),
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}));

describe('DashboardPage (F-023)', () => {
  beforeEach(() => {
    logoutMock.mockReset();
    pushMock.mockReset();
  });

  it('renders the dashboard heading', () => {
    const wrapper = mount(DashboardPage);

    expect(wrapper.text()).toContain('Dashboard');
  });

  it('logs out and redirects to /login', async () => {
    const wrapper = mount(DashboardPage);

    await wrapper.get('button[type="button"]').trigger('click');
    await flushPromises();

    expect(logoutMock).toHaveBeenCalledTimes(1);
    expect(pushMock).toHaveBeenCalledWith('/login');
  });
});
