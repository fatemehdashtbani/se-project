import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import LoginPage from '../LoginPage.vue';
import { ApiError } from '@/shared/api/client';

const { authStore, loginMock } = vi.hoisted(() => {
  const loginMock = vi.fn();
  return {
    loginMock,
    authStore: {
      user: null as {
        id: string;
        email: string;
        role: string;
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

const VALID_EMAIL = 'user@example.com';
const VALID_PASSWORD = 'secret123';

function fillForm(wrapper: ReturnType<typeof mount>, email: string, password: string) {
  const emailInput = wrapper.get('input[type="email"]');
  const passwordInput = wrapper.get('input[type="password"]');
  return Promise.all([emailInput.setValue(email), passwordInput.setValue(password)]);
}

async function submit(wrapper: ReturnType<typeof mount>) {
  await wrapper.get('form').trigger('submit.prevent');
}

describe('LoginPage (F-002)', () => {
  beforeEach(() => {
    loginMock.mockReset();
    authStore.user = null;
    authStore.isLoading = false;
  });

  it('renders the email and password inputs', () => {
    const wrapper = mount(LoginPage);

    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
  });

  it('renders the submit button with Persian text "ورود"', () => {
    const wrapper = mount(LoginPage);

    const button = wrapper.get('button[type="submit"]');
    expect(button.text()).toBe('ورود');
  });

  it('renders the "فراموشی رمز عبور" and "ثبت‌نام" links', () => {
    const wrapper = mount(LoginPage);

    const linkTexts = wrapper.findAll('a').map((link) => link.text());
    expect(linkTexts).toContain('فراموشی رمز عبور');
    expect(linkTexts).toContain('ثبت‌نام');
  });

  it('shows a Persian error for the email when the form is submitted empty', async () => {
    const wrapper = mount(LoginPage);

    await submit(wrapper);

    expect(wrapper.text()).toContain('ایمیل الزامی است');
  });

  it('shows a Persian error when the password is shorter than 8 characters', async () => {
    const wrapper = mount(LoginPage);

    await fillForm(wrapper, VALID_EMAIL, 'short');
    await submit(wrapper);

    expect(wrapper.text()).toContain('رمز عبور باید حداقل ۸ کاراکتر باشد');
  });

  it('shows a Persian error when the email is malformed', async () => {
    const wrapper = mount(LoginPage);

    await fillForm(wrapper, 'notanemail', VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.text()).toContain('فرمت ایمیل معتبر نیست');

    await fillForm(wrapper, 'foo@', VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.text()).toContain('فرمت ایمیل معتبر نیست');
    expect(wrapper.emitted('submit')).toBeUndefined();
  });

  it('shows no errors and emits submit when the form is fully valid', async () => {
    const wrapper = mount(LoginPage);

    await fillForm(wrapper, 'test@example.com', 'password123');
    await submit(wrapper);

    expect(wrapper.findAll('[role="alert"]')).toHaveLength(0);
    expect(wrapper.emitted('submit')).toEqual([
      [{ email: 'test@example.com', password: 'password123' }],
    ]);
  });

  it('emits a submit event with the credentials when the form is valid', async () => {
    const wrapper = mount(LoginPage);

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.emitted('submit')).toEqual([
      [{ email: VALID_EMAIL, password: VALID_PASSWORD }],
    ]);
  });

  it('submits the credentials through the auth store', async () => {
    const wrapper = mount(LoginPage);

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    expect(loginMock).toHaveBeenCalledWith(VALID_EMAIL, VALID_PASSWORD);
  });

  it('shows the Persian message when the credentials are rejected', async () => {
    loginMock.mockRejectedValueOnce(
      new ApiError(401, 'INVALID_CREDENTIALS', 'Invalid email or password'),
    );

    const wrapper = mount(LoginPage);

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);
    await flushPromises();

    const alerts = wrapper.findAll('[role="alert"]');
    expect(alerts).toHaveLength(1);
    expect(alerts[0].text()).toBe('ایمیل یا رمز عبور نادرست است');
  });

  it('disables the submit button while a login is in flight', () => {
    authStore.isLoading = true;

    const wrapper = mount(LoginPage);

    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined();
  });
});
