import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import ProfilePage from '../ProfilePage.vue';
import { ApiError } from '@/shared/api/client';
import type { UserRole } from '@/stores/auth';

const { authStore, updateTimezoneMock } = vi.hoisted(() => {
  const updateTimezoneMock = vi.fn();
  return {
    updateTimezoneMock,
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: UserRole;
        timezone: string;
      } | null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      init: vi.fn(),
      updateTimezone: updateTimezoneMock,
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

const USER = {
  id: '6f0f8f2e-8f6a-4d0e-9d3f-2b1c0a9e8d7c',
  email: 'user@example.com',
  role: 'user' as UserRole,
  timezone: 'Asia/Tehran',
};

const SUCCESS_MESSAGE = 'منطقه زمانی با موفقیت ذخیره شد';
const VALIDATION_MESSAGE = 'اطلاعات وارد شده معتبر نیست';

async function submitForm(wrapper: ReturnType<typeof mount>): Promise<void> {
  await wrapper.get('form').trigger('submit');
  await flushPromises();
}

describe('ProfilePage (F-004)', () => {
  beforeEach(() => {
    updateTimezoneMock.mockReset();
    authStore.user = { ...USER };
    authStore.isLoading = false;
  });

  it('renders the current email', () => {
    const wrapper = mount(ProfilePage);

    expect(wrapper.text()).toContain(USER.email);
  });

  it('pre-selects the current timezone in the dropdown', () => {
    const wrapper = mount(ProfilePage);

    const select = wrapper.get('select').element as HTMLSelectElement;

    expect(select.value).toBe(USER.timezone);
  });

  it('saves the selected timezone through the store', async () => {
    const wrapper = mount(ProfilePage);

    await wrapper.get('select').setValue('Europe/London');
    await submitForm(wrapper);

    expect(updateTimezoneMock).toHaveBeenCalledWith('Europe/London');
  });

  it('shows a Persian success message after saving', async () => {
    updateTimezoneMock.mockResolvedValueOnce(undefined);

    const wrapper = mount(ProfilePage);
    await submitForm(wrapper);

    expect(wrapper.text()).toContain(SUCCESS_MESSAGE);
  });

  it('shows a Persian error message when the backend rejects the zone', async () => {
    updateTimezoneMock.mockRejectedValueOnce(
      new ApiError(422, 'VALIDATION_ERROR', 'Invalid IANA timezone'),
    );

    const wrapper = mount(ProfilePage);
    await submitForm(wrapper);

    expect(wrapper.text()).toContain(VALIDATION_MESSAGE);
    expect(wrapper.text()).not.toContain(SUCCESS_MESSAGE);
  });

  it('keeps a stored timezone that is missing from the curated list selectable', () => {
    authStore.user = { ...USER, timezone: 'Antarctica/Troll' };

    const wrapper = mount(ProfilePage);

    const select = wrapper.get('select').element as HTMLSelectElement;
    const values = Array.from(select.options).map((option) => option.value);

    expect(values).toContain('Antarctica/Troll');
    expect(select.value).toBe('Antarctica/Troll');
  });
});
