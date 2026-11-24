import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import DashboardPage from '../DashboardPage.vue';
import ProfileIcon from '@/components/icons/ProfileIcon.vue';
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
        first_name: string | null;
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

describe('DashboardPage (F-023, F-026)', () => {
  beforeEach(() => {
    logoutMock.mockReset();
    pushMock.mockReset();
    authStore.user = {
      id: '6f0f8f2e-8f6a-4d0e-9d3f-2b1c0a9e8d7c',
      email: 'user@example.com',
      role: 'user',
      timezone: 'UTC',
      first_name: 'سارا',
    };
    authStore.isLoading = false;
  });

  function mountPage() {
    return mount(DashboardPage, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    });
  }

  it('renders the app name and the dashboard heading', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain('روتین کده');
    expect(wrapper.text()).toContain('داشبورد');
  });

  it('links to the profile page with the profile icon', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);

    expect(link.exists()).toBe(true);
    expect(link.props('to')).toBe('/profile');
    expect(link.attributes('aria-label')).toBe('پروفایل');
    expect(link.findComponent(ProfileIcon).exists()).toBe(true);
  });

  it('uses a dark background for the shell and top bar', () => {
    const wrapper = mountPage();

    expect(wrapper.get('div').classes()).toContain('bg-slate-900');
    expect(wrapper.get('header').classes()).toContain('bg-slate-900');
  });

  it('renders the logout control with Persian text', () => {
    const wrapper = mountPage();

    expect(wrapper.get('button[type="button"]').text()).toBe('خروج از حساب');
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
