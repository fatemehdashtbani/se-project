import { describe, expect, it, vi } from 'vitest';
import { mount, RouterLinkStub } from '@vue/test-utils';
import AdminHome from '../admin/AdminHome.vue';
import AdminSectionPage from '../admin/AdminSectionPage.vue';
import ForbiddenPage from '../ForbiddenPage.vue';

const { authStore, route } = vi.hoisted(() => ({
  authStore: {
    user: {
      id: 'user-id',
      email: 'user@example.com',
      role: 'user' as const,
      timezone: 'UTC',
      username: 'sara',
      first_name: 'سارا',
      last_name: null,
      phone_number: null,
    },
    isLoading: false,
    logout: vi.fn(),
  },
  route: { meta: { title: 'مدیریت کاربران' }, query: { required: 'admin' } },
}));

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRoute: () => route,
}));

describe('admin pages (F-030)', () => {
  it('renders the admin landing as an honest placeholder', () => {
    const wrapper = mount(AdminHome);

    expect(wrapper.text()).toContain('پنل مدیریت');
    expect(wrapper.text()).toContain('این بخش در حال توسعه است');
  });

  it('renders section placeholders using the route title', () => {
    const wrapper = mount(AdminSectionPage);

    expect(wrapper.text()).toContain('مدیریت کاربران');
    expect(wrapper.text()).toContain('این بخش در حال توسعه است');
  });

  it('shows a Persian access-denied page with a route back to the caller panel', () => {
    const wrapper = mount(ForbiddenPage, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    });

    expect(wrapper.text()).toContain('دسترسی غیرمجاز');
    expect(wrapper.text()).toContain('مدیر سامانه');
    expect(wrapper.text()).toContain('کاربر');
    expect(wrapper.findComponent(RouterLinkStub).props('to')).toBe('/dashboard');
  });
});
