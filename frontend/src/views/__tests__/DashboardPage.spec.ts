import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import DashboardPage from '../DashboardPage.vue';
import type { UserRole } from '@/stores/auth';

const { authStore, logoutMock, pushMock } = vi.hoisted(() => {
  const logoutMock = vi.fn();
  return {
    logoutMock,
    pushMock: vi.fn(),
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: UserRole;
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

  function mountPage() {
    return mount(DashboardPage, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    });
  }

  it('renders the dashboard heading', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain('Dashboard');
  });

  it('links to the profile page', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);

    expect(link.exists()).toBe(true);
    expect(link.props('to')).toBe('/profile');
    expect(link.text()).toBe('پروفایل');
  });

  it('logs out and redirects to /login', async () => {
    const wrapper = mountPage();

    await wrapper.get('button[type="button"]').trigger('click');
    await flushPromises();

    expect(logoutMock).toHaveBeenCalledTimes(1);
    expect(pushMock).toHaveBeenCalledWith('/login');
  });

  it('redirects to /login even when the logout request fails', async () => {
    logoutMock.mockRejectedValueOnce(new Error('network down'));

    const wrapper = mountPage();

    await wrapper.get('button[type="button"]').trigger('click');
    await flushPromises();

    expect(pushMock).toHaveBeenCalledWith('/login');
  });
});
