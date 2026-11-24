import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import LoginPage from '../LoginPage.vue';
import { ApiError } from '@/shared/api/client';
import type { UserRole } from '@/stores/auth';

const { authStore, loginMock, pushMock } = vi.hoisted(() => {
  const loginMock = vi.fn();
  return {
    loginMock,
    pushMock: vi.fn(),
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: UserRole;
        timezone: string;
      } | null,
      isLoading: false,
      login: loginMock,
      logout: vi.fn(),
      init: vi.fn(),
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}));

const VALID_EMAIL = 'user@example.com';
const VALID_PHONE = '09123456789';
const VALID_PASSWORD = 'secret123';

function fillForm(
  wrapper: ReturnType<typeof mount>,
  identifier: string,
  password: string,
) {
  const identifierInput = wrapper.get('#identifier');
  const passwordInput = wrapper.get('input[type="password"]');
  return Promise.all([identifierInput.setValue(identifier), passwordInput.setValue(password)]);
}

async function submit(wrapper: ReturnType<typeof mount>) {
  await wrapper.get('form').trigger('submit.prevent');
}

function mountPage() {
  return mount(LoginPage, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

function mobileTab(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((button) => button.text().includes('موبایل'));
}

describe('LoginPage (F-002, F-026)', () => {
  beforeEach(() => {
    loginMock.mockReset();
    pushMock.mockReset();
    authStore.user = null;
    authStore.isLoading = false;
  });

  it('renders the email and password inputs', () => {
    const wrapper = mountPage();

    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
  });

  it('renders the submit button with Persian text "ورود"', () => {
    const wrapper = mountPage();

    const button = wrapper.get('button[type="submit"]');
    expect(button.text()).toBe('ورود');
  });

  it('links to the forgot-password and registration pages', () => {
    const wrapper = mountPage();

    const links = wrapper.findAllComponents(RouterLinkStub);
    const byText = (text: string) => links.find((link) => link.text() === text);

    expect(byText('فراموشی رمز عبور؟')?.props('to')).toBe('/forgot-password');
    expect(byText('ثبت‌نام')?.props('to')).toBe('/register');
  });

  it('offers a working email/mobile toggle', async () => {
    const wrapper = mountPage();

    const mobile = mobileTab(wrapper);
    expect(mobile).toBeDefined();
    expect(mobile?.attributes('disabled')).toBeUndefined();

    await mobile?.trigger('click');
    await flushPromises();

    expect(wrapper.get('#identifier').attributes('type')).toBe('tel');
    expect(wrapper.text()).toContain('شماره تلفن');
  });

  it('switches back from mobile to email', async () => {
    const wrapper = mountPage();

    await mobileTab(wrapper)?.trigger('click');
    await flushPromises();

    const emailTab = wrapper.findAll('button').find((button) => button.text() === 'ایمیل');
    await emailTab?.trigger('click');
    await flushPromises();

    expect(wrapper.get('#identifier').attributes('type')).toBe('email');
  });

  it('renders a remember-me checkbox', async () => {
    const wrapper = mountPage();

    const checkbox = wrapper.get('input[type="checkbox"]');
    expect(wrapper.text()).toContain('مرا به خاطر بسپار');

    await checkbox.setValue(true);
    expect((checkbox.element as HTMLInputElement).checked).toBe(true);
  });

  it('shows a Persian error for the email when the form is submitted empty', async () => {
    const wrapper = mountPage();

    await submit(wrapper);

    expect(wrapper.text()).toContain('ایمیل الزامی است');
  });

  it('shows a Persian error when the password is shorter than 8 characters', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, 'short');
    await submit(wrapper);

    expect(wrapper.text()).toContain('رمز عبور باید حداقل ۸ کاراکتر باشد');
  });

  it('shows a Persian error when the email is malformed', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, 'notanemail', VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.text()).toContain('فرمت ایمیل معتبر نیست');

    await fillForm(wrapper, 'foo@', VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.text()).toContain('فرمت ایمیل معتبر نیست');
    expect(wrapper.emitted('submit')).toBeUndefined();
  });

  it('shows a Persian error when the mobile number is malformed', async () => {
    const wrapper = mountPage();

    await mobileTab(wrapper)?.trigger('click');
    await flushPromises();

    await fillForm(wrapper, 'not-a-phone', VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.text()).toContain('شماره تلفن معتبر نیست');
    expect(loginMock).not.toHaveBeenCalled();
  });

  it('shows no errors and emits the email identifier when the form is valid', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, 'test@example.com', 'password123');
    await submit(wrapper);

    expect(wrapper.findAll('[role="alert"]')).toHaveLength(0);
    expect(wrapper.emitted('submit')).toEqual([
      [{ identifier: 'test@example.com', password: 'password123' }],
    ]);
  });

  it('submits the email credentials through the auth store', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    expect(loginMock).toHaveBeenCalledWith(VALID_EMAIL, VALID_PASSWORD);
  });

  it('submits a normalized phone number as the identifier', async () => {
    const wrapper = mountPage();

    await mobileTab(wrapper)?.trigger('click');
    await flushPromises();

    await fillForm(wrapper, '0912 345 6789', VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    expect(loginMock).toHaveBeenCalledWith(VALID_PHONE, VALID_PASSWORD);
    expect(wrapper.emitted('submit')).toEqual([
      [{ identifier: VALID_PHONE, password: VALID_PASSWORD }],
    ]);
  });

  it('shows the Persian message when the credentials are rejected', async () => {
    loginMock.mockRejectedValueOnce(
      new ApiError(401, 'INVALID_CREDENTIALS', 'Invalid credentials'),
    );

    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    const alerts = wrapper.findAll('[role="alert"]');
    expect(alerts).toHaveLength(1);
    expect(alerts[0].text()).toBe('ایمیل یا رمز عبور نادرست است');
  });

  it('disables the submit button while a login is in flight', () => {
    authStore.isLoading = true;

    const wrapper = mountPage();

    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined();
  });

  it('renders the reference-style Persian heading', () => {
    const wrapper = mountPage();

    expect(wrapper.text()).toContain('ورود به حساب');
    expect(wrapper.text()).toContain('برای مدیریت روتینهای خود وارد شوید');
  });

  it('redirects to the dashboard after a successful login', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    expect(pushMock).toHaveBeenCalledWith('/dashboard');
  });

  it('redirects an admin to the admin panel after a successful login', async () => {
    authStore.user = {
      id: 'admin-id',
      email: VALID_EMAIL,
      role: 'admin',
      timezone: 'UTC',
    };
    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    expect(pushMock).toHaveBeenCalledWith('/admin');
  });
});
