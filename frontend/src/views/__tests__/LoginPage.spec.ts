import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import LoginPage from '../LoginPage.vue';

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

  it('emits a submit event with the credentials when the form is valid', async () => {
    const wrapper = mount(LoginPage);

    await fillForm(wrapper, VALID_EMAIL, VALID_PASSWORD);
    await submit(wrapper);

    expect(wrapper.emitted('submit')).toEqual([
      [{ email: VALID_EMAIL, password: VALID_PASSWORD }],
    ]);
  });
});
