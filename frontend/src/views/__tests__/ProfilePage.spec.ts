import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import ProfilePage from '../ProfilePage.vue';
import HomeIcon from '@/components/icons/HomeIcon.vue';
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

const TIMEZONE_SUCCESS_MESSAGE = 'منطقه زمانی با موفقیت ذخیره شد';
const PROFILE_SUCCESS_MESSAGE = 'اطلاعات با موفقیت ذخیره شد';
const PASSWORD_SUCCESS_MESSAGE = 'رمز عبور با موفقیت تغییر کرد';
const VALIDATION_MESSAGE = 'اطلاعات وارد شده معتبر نیست';

function mountPage() {
  return mount(ProfilePage, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

function passwordToggle(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((button) => button.text() === 'تغییر رمز عبور');
}

describe('ProfilePage (F-004, F-026)', () => {
  beforeEach(() => {
    updateTimezoneMock.mockReset();
    authStore.user = { ...USER };
    authStore.isLoading = false;
  });

  it('links back to the dashboard from the top-left home icon', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);

    expect(link.exists()).toBe(true);
    expect(link.props('to')).toBe('/dashboard');
    expect(link.attributes('aria-label')).toBe('بازگشت به داشبورد');
    expect(link.findComponent(HomeIcon).exists()).toBe(true);
  });

  it('renders the profile fields as editable inputs pre-filled from the user', () => {
    const wrapper = mountPage();

    const firstName = wrapper.get('#profile-first-name').element as HTMLInputElement;
    const lastName = wrapper.get('#profile-last-name').element as HTMLInputElement;
    const phone = wrapper.get('#profile-phone').element as HTMLInputElement;

    expect(firstName.value).toBe(USER.first_name);
    expect(lastName.value).toBe(USER.last_name);
    expect(phone.value).toBe(USER.phone_number);
  });

  it('keeps the email visible and read-only', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain(USER.email);
    expect(wrapper.find('input#profile-email').exists()).toBe(false);
  });

  it('leaves the inputs empty when the account has no stored profile', () => {
    authStore.user = { ...USER, first_name: null, last_name: null, phone_number: null };

    const wrapper = mountPage();

    const firstName = wrapper.get('#profile-first-name').element as HTMLInputElement;
    expect(firstName.value).toBe('');
  });

  it('saves the profile locally with a Persian success message and no API call', async () => {
    const wrapper = mountPage();

    await wrapper.get('#profile-first-name').setValue('نگار');
    await wrapper.get('#profile-form').trigger('submit');
    await flushPromises();

    expect(wrapper.get('[role="status"]').text()).toBe(PROFILE_SUCCESS_MESSAGE);
    expect(updateTimezoneMock).not.toHaveBeenCalled();
  });

  it('offers an active change-password button', () => {
    const wrapper = mountPage();

    const toggle = passwordToggle(wrapper);

    expect(toggle).toBeDefined();
    expect(toggle?.attributes('disabled')).toBeUndefined();
  });

  it('toggles the mock password form with its three inputs', async () => {
    const wrapper = mountPage();

    expect(wrapper.find('#password-form').exists()).toBe(false);

    await passwordToggle(wrapper)?.trigger('click');

    expect(wrapper.find('#password-form').exists()).toBe(true);
    expect(wrapper.find('#current-password').exists()).toBe(true);
    expect(wrapper.find('#new-password').exists()).toBe(true);
    expect(wrapper.find('#confirm-new-password').exists()).toBe(true);

    await passwordToggle(wrapper)?.trigger('click');
    expect(wrapper.find('#password-form').exists()).toBe(false);
  });

  it('shows a Persian success message and closes the form after a mock password change', async () => {
    const wrapper = mountPage();

    await passwordToggle(wrapper)?.trigger('click');
    await wrapper.get('#current-password').setValue('secret123');
    await wrapper.get('#new-password').setValue('new-secret123');
    await wrapper.get('#confirm-new-password').setValue('new-secret123');
    await wrapper.get('#password-form').trigger('submit');
    await flushPromises();

    expect(wrapper.get('[role="status"]').text()).toBe(PASSWORD_SUCCESS_MESSAGE);
    expect(wrapper.find('#password-form').exists()).toBe(false);
  });

  it('uses the dark theme for the page and inputs', () => {
    const wrapper = mountPage();

    expect(wrapper.get('div').classes()).toContain('bg-slate-900');
    expect(wrapper.get('select').classes()).toContain('bg-slate-800');
    expect(wrapper.get('#profile-first-name').classes()).toContain('bg-slate-800');
  });

  it('pre-selects the current timezone in the dropdown', () => {
    const wrapper = mountPage();

    const select = wrapper.get('select').element as HTMLSelectElement;

    expect(select.value).toBe(USER.timezone);
  });

  it('saves the selected timezone through the store', async () => {
    const wrapper = mountPage();

    await wrapper.get('select').setValue('Europe/London');
    await wrapper.get('#timezone-form').trigger('submit');
    await flushPromises();

    expect(updateTimezoneMock).toHaveBeenCalledWith('Europe/London');
  });

  it('shows a Persian success message after saving the timezone', async () => {
    updateTimezoneMock.mockResolvedValueOnce(undefined);

    const wrapper = mountPage();
    await wrapper.get('#timezone-form').trigger('submit');
    await flushPromises();

    expect(wrapper.text()).toContain(TIMEZONE_SUCCESS_MESSAGE);
  });

  it('shows a Persian error message when the backend rejects the zone', async () => {
    updateTimezoneMock.mockRejectedValueOnce(
      new ApiError(422, 'VALIDATION_ERROR', 'Invalid IANA timezone'),
    );

    const wrapper = mountPage();
    await wrapper.get('#timezone-form').trigger('submit');
    await flushPromises();

    expect(wrapper.text()).toContain(VALIDATION_MESSAGE);
    expect(wrapper.text()).not.toContain(TIMEZONE_SUCCESS_MESSAGE);
  });

  it('keeps a stored timezone that is missing from the curated list selectable', () => {
    authStore.user = { ...USER, timezone: 'Antarctica/Troll' };

    const wrapper = mountPage();

    const select = wrapper.get('select').element as HTMLSelectElement;
    const values = Array.from(select.options).map((option) => option.value);

    expect(values).toContain('Antarctica/Troll');
    expect(select.value).toBe('Antarctica/Troll');
  });
});
