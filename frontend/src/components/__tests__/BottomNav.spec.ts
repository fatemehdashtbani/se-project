import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import BottomNav from '../BottomNav.vue';
import ProfileIcon from '@/components/icons/ProfileIcon.vue';
import LogoutIcon from '@/components/icons/LogoutIcon.vue';
import ChecklistIcon from '@/components/icons/ChecklistIcon.vue';
import CalendarIcon from '@/components/icons/CalendarIcon.vue';
import NoteIcon from '@/components/icons/NoteIcon.vue';

const { authStore, logoutMock, pushMock } = vi.hoisted(() => {
  const logoutMock = vi.fn();
  return { authStore: { logout: logoutMock }, logoutMock, pushMock: vi.fn() };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}));

describe('BottomNav (F-029)', () => {
  beforeEach(() => {
    logoutMock.mockReset();
    pushMock.mockReset();
  });

  function mountNav() {
    return mount(BottomNav, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    });
  }

  it('renders a fixed dark-theme bar with evenly spaced items', () => {
    const wrapper = mountNav();

    const nav = wrapper.get('nav');
    expect(nav.classes()).toContain('fixed');
    expect(nav.classes()).toContain('bottom-0');
    expect(nav.classes()).toContain('left-0');
    expect(nav.classes()).toContain('w-full');
    expect(nav.classes()).toContain('z-50');
    expect(nav.classes()).toContain('bg-slate-900');
    expect(nav.classes()).toContain('border-t');
    expect(nav.classes()).toContain('border-slate-700');

    const items = nav.get('div');
    expect(items.classes()).toContain('flex');
    expect(items.classes()).toContain('justify-around');
    expect(items.classes()).toContain('items-center');
    expect(items.classes()).toContain('py-3');
  });

  it('links the dashboard, the three personal tools, and the profile', () => {
    const wrapper = mountNav();

    const links = wrapper.findAllComponents(RouterLinkStub);

    expect(links).toHaveLength(6);
    expect(links.map((link) => link.props('to'))).toEqual([
      '/dashboard',
      '/dashboard',
      '/checklist',
      '/calendar',
      '/notes',
      '/profile',
    ]);

    for (const label of [
      'خانه',
      'روتین‌ها',
      'چک‌لیست',
      'تقویم',
      'یادداشت‌ها',
      'پروفایل',
      'خروج',
    ]) {
      expect(wrapper.text()).toContain(label);
    }
  });

  it('uses the profile, logout and personal-tool icon components', () => {
    const wrapper = mountNav();

    expect(wrapper.findComponent(ProfileIcon).exists()).toBe(true);
    expect(wrapper.findComponent(LogoutIcon).exists()).toBe(true);
    expect(wrapper.findComponent(ChecklistIcon).exists()).toBe(true);
    expect(wrapper.findComponent(CalendarIcon).exists()).toBe(true);
    expect(wrapper.findComponent(NoteIcon).exists()).toBe(true);
  });

  it('logs out and redirects to /login', async () => {
    const wrapper = mountNav();

    await wrapper.get('button[aria-label="خروج"]').trigger('click');
    await flushPromises();

    expect(logoutMock).toHaveBeenCalledTimes(1);
    expect(pushMock).toHaveBeenCalledWith('/login');
  });

  it('redirects to /login even when the logout request fails', async () => {
    logoutMock.mockRejectedValueOnce(new Error('network down'));
    const wrapper = mountNav();

    await wrapper.get('button[aria-label="خروج"]').trigger('click');
    await flushPromises();

    expect(pushMock).toHaveBeenCalledWith('/login');
  });
});
