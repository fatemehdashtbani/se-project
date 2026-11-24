import { describe, expect, it, vi } from 'vitest';
import { mount, RouterLinkStub } from '@vue/test-utils';
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
}));

describe('AdminLayout (F-030)', () => {
  it('renders the sidebar beside the routed admin content', () => {
    const wrapper = mount(AdminLayout, {
      global: {
        stubs: { RouterLink: RouterLinkStub, RouterView: true },
      },
    });

    expect(wrapper.findComponent(AdminSidebar).exists()).toBe(true);
    expect(wrapper.get('main').classes()).toContain('min-w-0');
    expect(wrapper.get('div').attributes('dir')).toBe('rtl');
    expect(wrapper.text()).toContain('پنل مدیریت');
  });

  it('does not render the bottom navigation used by regular pages', () => {
    const wrapper = mount(AdminLayout, {
      global: {
        stubs: { RouterLink: RouterLinkStub, RouterView: true },
      },
    });

    expect(wrapper.find('nav').exists()).toBe(false);
  });
});
