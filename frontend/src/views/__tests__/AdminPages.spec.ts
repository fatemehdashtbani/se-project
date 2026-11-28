import { describe, expect, it, vi } from 'vitest';
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils';
import ElementPlus from 'element-plus';
import AdminHome from '../admin/AdminHome.vue';
import ForbiddenPage from '../ForbiddenPage.vue';
import type { DashboardData } from '@/stores/admin';

const { adminStore } = vi.hoisted(() => {
  const dashboard = {
    total_users: 42,
    active_users: 38,
    banned_users: 2,
    total_routines: 120,
    total_mentors: 5,
    pending_mentor_requests: 3,
    total_mentor_programs: 9,
    active_mentorships: 7,
    active_today: 11,
    total_templates: 4,
    total_categories: 6,
    total_broadcasts: 1,
    activity: [
      { date: '2026-11-27', signups: 2, routines: 5, active_users: 4 },
      { date: '2026-11-28', signups: 1, routines: 3, active_users: 6 },
    ],
  } as DashboardData;

  return {
    adminStore: {
      dashboard,
      isLoading: false,
      fetchDashboard: vi.fn().mockResolvedValue(undefined),
    },
  };
});

vi.mock('@/stores/admin', () => ({
  useAdminStore: () => adminStore,
}));

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({ user: { role: 'user' }, isLoading: false, logout: vi.fn() }),
}));

vi.mock('vue-router', () => ({
  useRoute: () => ({ meta: { title: 'مدیریت کاربران' }, query: { required: 'admin' } }),
  useRouter: () => ({ push: vi.fn() }),
}));

describe('admin dashboard (F-037)', () => {
  it('renders the platform counters returned by the API', async () => {
    const wrapper = mount(AdminHome, { global: { plugins: [ElementPlus] } });
    await flushPromises();

    expect(adminStore.fetchDashboard).toHaveBeenCalledTimes(1);
    expect(wrapper.text()).toContain('نمای کلی سامانه');
    expect(wrapper.text()).toContain('۴۲');
    expect(wrapper.text()).toContain('۱۲۰');
    expect(wrapper.text()).toContain('درخواست‌های منتور شدن');
    expect(wrapper.text()).toContain('کاربران فعال امروز');
    expect(wrapper.text()).toContain('۱۱');
  });
});

describe('forbidden page (F-030)', () => {
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
