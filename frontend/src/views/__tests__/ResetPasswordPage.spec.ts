import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import ResetPasswordPage from '../ResetPasswordPage.vue';
import { ApiError } from '@/shared/api/client';

const { authStore, resetPasswordMock, routeState } = vi.hoisted(() => {
  const resetPasswordMock = vi.fn();
  return {
    resetPasswordMock,
    routeState: { token: 'tok-123' },
    authStore: {
      user: null,
      isLoading: false,
      resetPassword: resetPasswordMock,
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: { token: routeState.token } }),
}));

function mountPage() {
  return mount(ResetPasswordPage, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  });
}

async function submit(wrapper: ReturnType<typeof mount>): Promise<void> {
  await wrapper.get('form').trigger('submit.prevent');
  await flushPromises();
}

describe('ResetPasswordPage (F-022)', () => {
  beforeEach(() => {
    resetPasswordMock.mockReset();
    routeState.token = 'tok-123';
  });

  it('renders both password fields and the submit button', () => {
    const wrapper = mountPage();

    expect(wrapper.findAll('input[type="password"]')).toHaveLength(2);
    expect(wrapper.get('button[type="submit"]').text()).toBe('ذخیره رمز عبور جدید');
  });

  it('shows an error instead of the form when the link has no token', () => {
    routeState.token = '';

    const wrapper = mountPage();

    expect(wrapper.find('form').exists()).toBe(false);
    expect(wrapper.get('[role="alert"]').text()).toBe(
      'لینک بازیابی رمز نامعتبر است یا منقضی شده است',
    );
  });

  it('blocks a short password and a mismatched confirmation without calling the API', async () => {
    const wrapper = mountPage();

    await wrapper.get('#new-password').setValue('short');
    await submit(wrapper);

    expect(wrapper.text()).toContain('رمز عبور باید حداقل ۸ کاراکتر باشد');
    expect(resetPasswordMock).not.toHaveBeenCalled();

    await wrapper.get('#new-password').setValue('new-password-123');
    await wrapper.get('#confirm-password').setValue('different-123');
    await submit(wrapper);

    expect(wrapper.text()).toContain('تکرار رمز عبور با رمز جدید یکسان نیست');
    expect(resetPasswordMock).not.toHaveBeenCalled();
  });

  it('sends the token and new password, then shows the success message', async () => {
    resetPasswordMock.mockResolvedValueOnce(undefined);

    const wrapper = mountPage();

    await wrapper.get('#new-password').setValue('new-password-123');
    await wrapper.get('#confirm-password').setValue('new-password-123');
    await submit(wrapper);

    expect(resetPasswordMock).toHaveBeenCalledWith('tok-123', 'new-password-123');
    expect(wrapper.get('[role="status"]').text()).toBe(
      'رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید.',
    );
    expect(wrapper.find('form').exists()).toBe(false);
  });

  it('shows a Persian error for an expired or used link', async () => {
    resetPasswordMock.mockRejectedValueOnce(
      new ApiError(400, 'INVALID_RESET_TOKEN', 'This password reset link is invalid.'),
    );

    const wrapper = mountPage();

    await wrapper.get('#new-password').setValue('new-password-123');
    await wrapper.get('#confirm-password').setValue('new-password-123');
    await submit(wrapper);

    expect(wrapper.get('[role="alert"]').text()).toBe(
      'لینک بازیابی رمز نامعتبر است یا منقضی شده است',
    );
  });

  it('links back to the login page', () => {
    const wrapper = mountPage();

    const link = wrapper.findComponent(RouterLinkStub);
    expect(link.props('to')).toBe('/login');
  });
});
