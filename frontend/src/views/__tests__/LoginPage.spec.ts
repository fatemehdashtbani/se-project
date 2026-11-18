import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import LoginPage from '../LoginPage.vue';

describe('LoginPage (placeholder)', () => {
  it('renders the coming-soon placeholder', () => {
    const wrapper = mount(LoginPage);
    expect(wrapper.find('[data-testid="placeholder"]').exists()).toBe(true);
  });
});
