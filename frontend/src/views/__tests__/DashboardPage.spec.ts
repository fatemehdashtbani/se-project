import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  RouterLinkStub,
  flushPromises,
  mount,
  type DOMWrapper,
  type VueWrapper,
} from '@vue/test-utils';
import DashboardPage from '../DashboardPage.vue';
import BottomNav from '@/components/BottomNav.vue';
import type { UserRole } from '@/stores/auth';
import type { Routine } from '@/stores/routine';

const {
  authStore,
  routineStore,
  fetchRoutinesMock,
  createRoutineMock,
  deleteRoutineMock,
} = vi.hoisted(() => {
  return {
    fetchRoutinesMock: vi.fn(),
    createRoutineMock: vi.fn(),
    deleteRoutineMock: vi.fn(),
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: UserRole;
        timezone: string;
        first_name: string | null;
        username: string | null;
      } | null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      init: vi.fn(),
    },
    routineStore: {
      routines: [] as Routine[],
      isLoading: false,
      fetchRoutines: vi.fn(),
      createRoutine: vi.fn(),
      deleteRoutine: vi.fn(),
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('@/stores/routine', () => ({
  useRoutineStore: () => routineStore,
}));

const SIGNED_IN_USER = {
  id: '6f0f8f2e-8f6a-4d0e-9d3f-2b1c0a9e8d7c',
  email: 'user@example.com',
  role: 'user' as UserRole,
  timezone: 'UTC',
  first_name: 'سارا',
  username: 'sara_ahmadi',
};

const ROUTINE: Routine = {
  id: '3f4a0d90-1b2c-4d3e-8f5a-6b7c8d9e0f1a',
  title: 'صبحانه',
  description: 'هر روز صبح ساعت ۷',
  is_active: true,
  created_at: '2026-11-24T06:00:00Z',
  updated_at: '2026-11-24T06:00:00Z',
};

function findButton(wrapper: VueWrapper, text: string): DOMWrapper<Element> {
  const button = wrapper.findAll('button').find((candidate) => candidate.text() === text);
  if (!button) {
    throw new Error(`Button with text "${text}" was not rendered`);
  }
  return button;
}

describe('DashboardPage (F-023, F-026, F-005)', () => {
  beforeEach(() => {
    fetchRoutinesMock.mockReset().mockResolvedValue(undefined);
    createRoutineMock.mockReset().mockResolvedValue(undefined);
    deleteRoutineMock.mockReset().mockResolvedValue(undefined);
    routineStore.fetchRoutines = fetchRoutinesMock;
    routineStore.createRoutine = createRoutineMock;
    routineStore.deleteRoutine = deleteRoutineMock;
    routineStore.routines = [];
    authStore.user = { ...SIGNED_IN_USER };
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

  it('greets the user by first name', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain(
      'کاربر سارا به روتین کده خوش آمدید.',
    );
    expect(wrapper.text()).not.toContain('به\u200cزودی');
  });

  it('falls back to the username, then to «کاربر»', () => {
    authStore.user = { ...SIGNED_IN_USER, first_name: null };
    expect(mountPage().text()).toContain('کاربر sara_ahmadi به روتین کده خوش آمدید');

    authStore.user = { ...SIGNED_IN_USER, first_name: null, username: null };
    expect(mountPage().text()).toContain('کاربر کاربر به روتین کده خوش آمدید');
  });

  it('keeps the header free of profile and logout controls', () => {
    const wrapper = mountPage();

    const header = wrapper.get('header');

    expect(header.text()).toContain('روتین کده');
    expect(header.findAll('button')).toHaveLength(0);
    expect(header.findAllComponents(RouterLinkStub)).toHaveLength(0);
    expect(wrapper.find('button[aria-label="خروج از حساب"]').exists()).toBe(false);
    expect(wrapper.find('[aria-label="پروفایل"]').exists()).toBe(false);
  });

  it('uses a dark background for the shell and top bar', () => {
    const wrapper = mountPage();

    expect(wrapper.get('div').classes()).toContain('bg-slate-900');
    expect(wrapper.get('header').classes()).toContain('bg-slate-900');
  });

  it('renders the shared bottom navigation', () => {
    const wrapper = mountPage();

    expect(wrapper.findComponent(BottomNav).exists()).toBe(true);
  });

  it('fetches routines when mounted', () => {
    mountPage();

    expect(fetchRoutinesMock).toHaveBeenCalledTimes(1);
  });

  it('shows the My Routines heading and the Persian empty state', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain('روتین‌های من');
    expect(wrapper.text()).toContain('هنوز هیچ روتینی نساخته\u200cاید');
    expect(wrapper.text()).not.toContain(ROUTINE.title);
  });

  it('renders each routine with its title, description, and delete control', async () => {
    routineStore.routines = [ROUTINE, { ...ROUTINE, id: 'second-id', title: 'ورزش', description: null }];
    const wrapper = mountPage();

    expect(wrapper.text()).toContain('صبحانه');
    expect(wrapper.text()).toContain('هر روز صبح ساعت ۷');
    expect(wrapper.text()).toContain('ورزش');
    expect(wrapper.findAll('button').filter((button) => button.text() === 'حذف')).toHaveLength(2);

    await findButton(wrapper, 'حذف').trigger('click');

    expect(deleteRoutineMock).toHaveBeenCalledWith(ROUTINE.id);
  });

  it('opens an inline form and saves a new routine', async () => {
    const wrapper = mountPage();

    expect(wrapper.find('input#routine-title').exists()).toBe(false);

    await findButton(wrapper, '+ روتین جدید').trigger('click');

    const titleInput = wrapper.get('input#routine-title');
    const descriptionInput = wrapper.get('textarea#routine-description');
    expect(wrapper.get('label[for="routine-title"]').text()).toBe('عنوان');

    await titleInput.setValue('خواب');
    await descriptionInput.setValue('هر شب ساعت ۱۱');
    await wrapper.get('form').trigger('submit');
    await flushPromises();

    expect(createRoutineMock).toHaveBeenCalledWith('خواب', 'هر شب ساعت ۱۱');
    expect(wrapper.find('input#routine-title').exists()).toBe(false);
  });

  it('does not submit a blank title', async () => {
    const wrapper = mountPage();
    await findButton(wrapper, '+ روتین جدید').trigger('click');

    await wrapper.get('form').trigger('submit');
    await flushPromises();

    expect(createRoutineMock).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain('عنوان روتین الزامی است.');
  });
});
