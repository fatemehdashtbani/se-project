import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils';
import AdminSidebar from '../AdminSidebar.vue';
import LogoutIcon from '@/components/icons/LogoutIcon.vue';
import type { User } from '@/stores/auth';

const { authStore, logoutMock, pushMock } = vi.hoisted(() => {
  const logoutMock = vi.fn();
  return {
    logoutMock,
    pushMock: vi.fn(),
    authStore: {
      user: null as User | null,
      isLoading: false,
      logout: logoutMock,
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}));

const ADMIN: User = {
  id: 'admin-id',
  email: 'admin@example.com',
  role: 'admin',
  timezone: 'UTC',
  username: 'admin',
  first_name: 'مدیر',
  last_name: 'سامانه',
  phone_number: null,
};

function mountSidebar() {
  return mount(AdminSidebar, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

describe('AdminSidebar (F-030)', () => {
  beforeEach(() => {
    logoutMock.mockReset();
    pushMock.mockReset();
    authStore.user = { ...ADMIN };
  });

  it('renders an RTL dark sidebar for the admin panel', () => {
    const wrapper = mountSidebar();

    const aside = wrapper.get('aside');
    expect(aside.attributes('dir')).toBe('rtl');
    expect(aside.classes()).toContain('bg-slate-900');
    expect(aside.classes()).toContain('h-screen');
    expect(wrapper.text()).toContain('روتین کده');
    expect(wrapper.text()).toContain('پنل مدیریت');
  });

  it('exposes management links and links back into the normal app', () => {
    const wrapper = mountSidebar();

    const targets = wrapper.findAllComponents(RouterLinkStub).map((link) => link.props('to'));

    expect(targets).toEqual([
      '/admin',
      '/admin/users',
      '/admin/mentor-applications',
      '/admin/plans',
      '/dashboard',
      '/profile',
    ]);
    expect(wrapper.text()).toContain('داشبورد');
    expect(wrapper.text()).toContain('کاربران');
    expect(wrapper.text()).toContain('درخواست‌های مربیگری');
    expect(wrapper.text()).toContain('اشتراکها');
    expect(wrapper.text()).toContain('بازگشت به روتینها');
    expect(wrapper.text()).toContain('پروفایل');
  });

  it('shows the signed-in admin and the dedicated logout icon', () => {
    const wrapper = mountSidebar();

    expect(wrapper.text()).toContain('مدیر');
    expect(wrapper.text()).toContain('مدیر سامانه');
    expect(wrapper.get('button[aria-label="خروج"]').findComponent(LogoutIcon).exists()).toBe(true);
  });

  it('logs out and returns to the login page', async () => {
    const wrapper = mountSidebar();

    await wrapper.get('button[aria-label="خروج"]').trigger('click');
    await flushPromises();

    expect(logoutMock).toHaveBeenCalledTimes(1);
    expect(pushMock).toHaveBeenCalledWith('/login');
  });

  it('still returns to login when the revoke request fails', async () => {
    logoutMock.mockRejectedValueOnce(new Error('network down'));
    const wrapper = mountSidebar();

    await wrapper.get('button[aria-label="خروج"]').trigger('click');
    await flushPromises();

    expect(pushMock).toHaveBeenCalledWith('/login');
  });
});
