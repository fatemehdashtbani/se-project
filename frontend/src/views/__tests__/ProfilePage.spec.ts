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
        username: string | null;
        first_name: string | null;
        last_name: string | null;
        phone_number: string | null;
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
  username: 'sara_ahmadi',
  first_name: 'سارا',
  last_name: 'احمدی',
  phone_number: '09121234567',
};

const SUCCESS_MESSAGE = 'منطقه زمانی با موفقیت ذخیره شد';
const VALIDATION_MESSAGE = 'اطلاعات وارد شده معتبر نیست';

async function submitForm(wrapper: ReturnType<typeof mount>): Promise<void> {
  await wrapper.get('form').trigger('submit');
  await flushPromises();
}

function passwordButton(wrapper: ReturnType<typeof mount>) {
  return wrapper
    .findAll('button')
    .find((button) => button.text().includes('تغییر رمز عبور'));
}

describe('ProfilePage (F-004, F-026)', () => {
  beforeEach(() => {
    updateTimezoneMock.mockReset();
    authStore.user = { ...USER };
    authStore.isLoading = false;
  });

  it('renders the read-only profile fields', () => {
    const wrapper = mount(ProfilePage);

    expect(wrapper.text()).toContain(USER.first_name);
    expect(wrapper.text()).toContain(USER.last_name);
    expect(wrapper.text()).toContain(USER.phone_number);
    expect(wrapper.text()).toContain(USER.email);
  });

  it('renders a placeholder for a profile field the account has not filled', () => {
    authStore.user = { ...USER, first_name: null };

    const wrapper = mount(ProfilePage);

    expect(wrapper.text()).toContain('—');
  });

  it('offers a disabled change-password placeholder', () => {
    const wrapper = mount(ProfilePage);

    const button = passwordButton(wrapper);

    expect(button).toBeDefined();
    expect(button?.attributes('disabled')).toBeDefined();
  });

  it('uses the dark theme for the page and inputs', () => {
    const wrapper = mount(ProfilePage);

    expect(wrapper.get('div').classes()).toContain('bg-slate-900');
    expect(wrapper.get('select').classes()).toContain('bg-slate-800');
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
