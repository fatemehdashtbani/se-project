import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import RegisterPage from '../RegisterPage.vue';
import { ApiError } from '@/shared/api/client';
import type { UserRole } from '@/stores/auth';

const { authStore, registerMock, pushMock } = vi.hoisted(() => {
  const registerMock = vi.fn();
  return {
    registerMock,
    pushMock: vi.fn(),
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: UserRole;
        timezone: string;
      } | null,
      isLoading: false,
      login: vi.fn(),
      register: registerMock,
      logout: vi.fn(),
      init: vi.fn(),
      updateTimezone: vi.fn(),
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}));

const MISMATCH_MESSAGE = 'رمز عبور و تکرار آن یکسان نیستند';
const EMAIL_TAKEN_MESSAGE = 'این ایمیل قبلاً ثبت شده است';
const USERNAME_TAKEN_MESSAGE = 'این نام کاربری قبلاً انتخاب شده است';
const FIRST_NAME_REQUIRED_MESSAGE = 'نام الزامی است';

const VALID = {
  firstName: 'سارا',
  lastName: 'احمدی',
  username: 'sara_ahmadi',
  phone: '0912 345 6789',
  email: 'new@example.com',
  password: 'secret123',
  confirmation: 'secret123',
};

function mountPage() {
  return mount(RegisterPage, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

async function fillForm(
  wrapper: ReturnType<typeof mount>,
  overrides: Partial<typeof VALID> = {},
): Promise<void> {
  const values = { ...VALID, ...overrides };

  await wrapper.get('#register-first-name').setValue(values.firstName);
  await wrapper.get('#register-last-name').setValue(values.lastName);
  await wrapper.get('#register-username').setValue(values.username);
  await wrapper.get('#register-phone').setValue(values.phone);
  await wrapper.get('input[type="email"]').setValue(values.email);

  const passwords = wrapper.findAll('input[type="password"]');
  await passwords[0].setValue(values.password);
  await passwords[1].setValue(values.confirmation);
}

async function submit(wrapper: ReturnType<typeof mount>): Promise<void> {
  await wrapper.get('form').trigger('submit');
  await flushPromises();
}

describe('RegisterPage (F-025)', () => {
  beforeEach(() => {
    registerMock.mockReset();
    pushMock.mockReset();
    authStore.user = null;
    authStore.isLoading = false;
  });

  it('renders the profile, email, and password inputs', () => {
    const wrapper = mountPage();

    expect(wrapper.find('#register-first-name').exists()).toBe(true);
    expect(wrapper.find('#register-last-name').exists()).toBe(true);
    expect(wrapper.find('#register-username').exists()).toBe(true);
    expect(wrapper.find('#register-phone').exists()).toBe(true);
    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.findAll('input[type="password"]')).toHaveLength(2);
  });

  it('refuses to submit when a required profile field is empty', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, { firstName: '   ' });
    await submit(wrapper);

    expect(wrapper.text()).toContain(FIRST_NAME_REQUIRED_MESSAGE);
    expect(registerMock).not.toHaveBeenCalled();
  });

  it('refuses to submit when the passwords do not match', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, { confirmation: 'different-password' });
    await submit(wrapper);

    expect(wrapper.text()).toContain(MISMATCH_MESSAGE);
    expect(registerMock).not.toHaveBeenCalled();
  });

  it('registers with the entered profile when the form is valid', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper);
    await submit(wrapper);

    expect(registerMock).toHaveBeenCalledWith({
      email: VALID.email,
      password: VALID.password,
      username: VALID.username,
      firstName: VALID.firstName,
      lastName: VALID.lastName,
      // The page strips the spaces people type into phone fields.
      phoneNumber: '09123456789',
    });
  });

  it('shows a Persian message when the email is already registered', async () => {
    registerMock.mockRejectedValueOnce(
      new ApiError(400, 'EMAIL_ALREADY_EXISTS', 'Email is already registered.'),
    );

    const wrapper = mountPage();

    await fillForm(wrapper);
    await submit(wrapper);

    const alerts = wrapper.findAll('[role="alert"]');
    expect(alerts).toHaveLength(1);
    expect(alerts[0].text()).toBe(EMAIL_TAKEN_MESSAGE);
  });

  it('shows a Persian message when the username is already taken', async () => {
    registerMock.mockRejectedValueOnce(
      new ApiError(400, 'USERNAME_ALREADY_EXISTS', 'Username is already taken.'),
    );

    const wrapper = mountPage();

    await fillForm(wrapper);
    await submit(wrapper);

    const alerts = wrapper.findAll('[role="alert"]');
    expect(alerts).toHaveLength(1);
    expect(alerts[0].text()).toBe(USERNAME_TAKEN_MESSAGE);
  });

  it('redirects to the dashboard after a successful registration', async () => {
    registerMock.mockResolvedValueOnce(undefined);

    const wrapper = mountPage();

    await fillForm(wrapper);
    await submit(wrapper);

    expect(pushMock).toHaveBeenCalledWith('/dashboard');
  });

  it('renders the reference-style Persian heading', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain('ایجاد حساب کاربری جدید');
    expect(wrapper.text()).toContain('با چند گام ساده روتین خود را آغاز کنید');
  });

  it('links to the login page', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);

    expect(link.exists()).toBe(true);
    expect(link.props('to')).toBe('/login');
  });

  it('uses the role-aware landing page after registration', async () => {
    // The backend owns role assignment; this only proves the redirect helper
    // is used instead of a hard-coded /dashboard push.
    authStore.user = {
      id: 'admin-id',
      email: VALID.email,
      role: 'admin',
      timezone: 'UTC',
    };
    const wrapper = mountPage();

    await fillForm(wrapper);
    await submit(wrapper);

    expect(pushMock).toHaveBeenCalledWith('/admin');
  });
});
