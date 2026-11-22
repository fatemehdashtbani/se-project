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

const VALID_EMAIL = 'new@example.com';
const VALID_PASSWORD = 'secret123';
const MISMATCH_MESSAGE = 'رمز عبور و تکرار آن یکسان نیستند';
const EMAIL_TAKEN_MESSAGE = 'این ایمیل قبلاً ثبت شده است';

function mountPage() {
  return mount(RegisterPage, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

async function fillForm(
  wrapper: ReturnType<typeof mount>,
  email: string,
  password: string,
  confirmation: string,
): Promise<void> {
  await wrapper.get('input[type="email"]').setValue(email);
  const passwordInputs = wrapper.findAll('input[type="password"]');
  await passwordInputs[0].setValue(password);
  await passwordInputs[1].setValue(confirmation);
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

  it('renders the email, password, and confirmation inputs', () => {
    const wrapper = mountPage();

    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.findAll('input[type="password"]')).toHaveLength(2);
  });

  it('refuses to submit when the passwords do not match', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD, 'different-password');
    await submit(wrapper);

    expect(wrapper.text()).toContain(MISMATCH_MESSAGE);
    expect(registerMock).not.toHaveBeenCalled();
  });

  it('registers with the entered email and password when the form is valid', async () => {
    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD, VALID_PASSWORD);
    await submit(wrapper);

    expect(registerMock).toHaveBeenCalledWith(VALID_EMAIL, VALID_PASSWORD);
  });

  it('shows a Persian message when the email is already registered', async () => {
    registerMock.mockRejectedValueOnce(
      new ApiError(400, 'EMAIL_ALREADY_EXISTS', 'Email is already registered.'),
    );

    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD, VALID_PASSWORD);
    await submit(wrapper);

    const alerts = wrapper.findAll('[role="alert"]');
    expect(alerts).toHaveLength(1);
    expect(alerts[0].text()).toBe(EMAIL_TAKEN_MESSAGE);
  });

  it('redirects to the dashboard after a successful registration', async () => {
    registerMock.mockResolvedValueOnce(undefined);

    const wrapper = mountPage();

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD, VALID_PASSWORD);
    await submit(wrapper);

    expect(pushMock).toHaveBeenCalledWith('/dashboard');
  });

  it('links to the login page', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);

    expect(link.exists()).toBe(true);
    expect(link.props('to')).toBe('/login');
  });
});
