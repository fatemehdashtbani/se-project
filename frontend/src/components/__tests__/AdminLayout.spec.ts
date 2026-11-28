import { describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ElementPlus from 'element-plus';
import AdminLayout from '../AdminLayout.vue';
import AdminSidebar from '../AdminSidebar.vue';

const { authStore } = vi.hoisted(() => ({
  authStore: {
    user: {
      id: 'admin-id',
      email: 'admin@example.com',
      role: 'admin' as const,
      timezone: 'UTC',
      username: 'admin',
      first_name: 'مدیر',
      last_name: 'سامانه',
      phone_number: null,
    },
    isLoading: false,
    logout: vi.fn(),
  },
}));

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ path: '/admin', meta: { title: 'داشبورد' } }),
}));

function mountLayout() {
  return mount(AdminLayout, {
    global: {
      plugins: [ElementPlus],
      stubs: { RouterView: true },
    },
  });
}

describe('AdminLayout (F-030, F-037)', () => {
  it('renders the sidebar beside the routed admin content', () => {
    const wrapper = mountLayout();

    expect(wrapper.findComponent(AdminSidebar).exists()).toBe(true);
    expect(wrapper.get('main').classes()).toContain('min-w-0');
    expect(wrapper.get('div').attributes('dir')).toBe('rtl');
    expect(wrapper.get('div').classes()).toContain('admin-shell');
    expect(wrapper.text()).toContain('پنل مدیریت');
    expect(wrapper.text()).toContain('داشبورد');
  });

  it('does not render the bottom navigation used by regular pages', () => {
    const wrapper = mountLayout();

    expect(wrapper.find('nav').exists()).toBe(false);
  });
});
