import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import ForgotPasswordPage from '../ForgotPasswordPage.vue';
import { ApiError } from '@/shared/api/client';

const { authStore, forgotPasswordMock } = vi.hoisted(() => {
  const forgotPasswordMock = vi.fn();
  return {
    forgotPasswordMock,
    authStore: {
      user: null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      init: vi.fn(),
      forgotPassword: forgotPasswordMock,
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

const VALID_EMAIL = 'user@example.com';
const SUCCESS_MESSAGE = 'لینک بازیابی ارسال شد';

function mountPage() {
  return mount(ForgotPasswordPage, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

async function submit(wrapper: ReturnType<typeof mount>): Promise<void> {
  await wrapper.get('form').trigger('submit.prevent');
  await flushPromises();
}

describe('ForgotPasswordPage (F-026)', () => {
  beforeEach(() => {
    forgotPasswordMock.mockReset();
  });

  it('renders an email input and the submit button', () => {
    const wrapper = mountPage();

    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.get('button[type="submit"]').text()).toBe('ارسال لینک بازیابی');
  });

  it('shows a Persian error and does not call the API for a malformed email', async () => {
    const wrapper = mountPage();

    await wrapper.get('input[type="email"]').setValue('notanemail');
    await submit(wrapper);

    expect(wrapper.text()).toContain('فرمت ایمیل معتبر نیست');
    expect(forgotPasswordMock).not.toHaveBeenCalled();
  });

  it('sends the email and shows the Persian success message', async () => {
    forgotPasswordMock.mockResolvedValueOnce(undefined);

    const wrapper = mountPage();

    await wrapper.get('input[type="email"]').setValue(VALID_EMAIL);
    await submit(wrapper);

    expect(forgotPasswordMock).toHaveBeenCalledWith(VALID_EMAIL);

    const status = wrapper.get('[role="status"]');
    expect(status.text()).toBe(SUCCESS_MESSAGE);
  });

  it('shows a Persian error when the backend rejects the request', async () => {
    forgotPasswordMock.mockRejectedValueOnce(
      new ApiError(422, 'VALIDATION_ERROR', 'Request validation failed.'),
    );

    const wrapper = mountPage();

    await wrapper.get('input[type="email"]').setValue(VALID_EMAIL);
    await submit(wrapper);

    expect(wrapper.get('[role="alert"]').text()).toBe('اطلاعات وارد شده معتبر نیست');
    expect(wrapper.text()).not.toContain(SUCCESS_MESSAGE);
  });

  it('links back to the login page', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);

    expect(link.exists()).toBe(true);
    expect(link.props('to')).toBe('/login');
  });
});
