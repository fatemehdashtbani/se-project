import { beforeEach, describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import ThemeToggle from '../ThemeToggle.vue';
import { applyTheme } from '@/shared/theme';

describe('ThemeToggle (F-032)', () => {
  beforeEach(() => {
    localStorage.clear();
    applyTheme('dark');
  });

  it('sits in the top-left corner and exposes an accessible label', () => {
    const wrapper = mount(ThemeToggle);

    expect(wrapper.get('button').classes()).toContain('left-4');
    expect(wrapper.get('button').classes()).toContain('top-4');
    expect(wrapper.get('button').attributes('aria-label')).toBe('فعال کردن حالت روشن');
    expect(wrapper.find('svg').exists()).toBe(true);
  });

  it('switches to the light theme when clicked', async () => {
    const wrapper = mount(ThemeToggle);

    await wrapper.get('button').trigger('click');

    expect(document.documentElement.dataset.theme).toBe('light');
    expect(wrapper.get('button').attributes('aria-label')).toBe('فعال کردن حالت تاریک');
  });
});
