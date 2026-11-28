import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import ElementPlus from 'element-plus';
import AdminSidebar from '../AdminSidebar.vue';
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
  useRoute: () => ({ path: '/admin/users' }),
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
    global: { plugins: [ElementPlus] },
  });
}

describe('AdminSidebar (F-030, F-037)', () => {
  beforeEach(() => {
    logoutMock.mockReset();
    pushMock.mockReset();
    authStore.user = { ...ADMIN };
  });

  it('renders an RTL purple sidebar for the admin panel', () => {
    const wrapper = mountSidebar();

    const aside = wrapper.get('aside');
    expect(aside.attributes('dir')).toBe('rtl');
    expect(aside.classes()).toContain('admin-sidebar');
    expect(aside.classes()).toContain('h-screen');
    expect(wrapper.text()).toContain('روتین کده');
    expect(wrapper.text()).toContain('پنل مدیریت');
  });

  it('exposes every management section and links back into the normal app', () => {
    const wrapper = mountSidebar();

    const labels = wrapper
      .findAll('.el-menu-item')
      .map((item) => item.text().trim());

    expect(labels).toEqual([
      'داشبورد',
      'کاربران',
      'منتورها و منتورشیپ',
      'محتوا و روتین‌ها',
      'سیستم و لاگ‌ها',
      'بازگشت به روتین‌ها',
      'پروفایل',
    ]);
  });

  it('marks the current section as active', () => {
    const wrapper = mountSidebar();

    expect(wrapper.get('.el-menu-item.is-active').text()).toContain('کاربران');
  });

  it('shows the signed-in admin and a dedicated logout control', () => {
    const wrapper = mountSidebar();

    expect(wrapper.text()).toContain('مدیر سامانه');
    expect(wrapper.find('button[aria-label="خروج"]').exists()).toBe(true);
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
