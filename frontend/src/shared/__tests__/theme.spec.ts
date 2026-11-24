import { beforeEach, describe, expect, it } from 'vitest';
import { applyTheme, initTheme, useTheme } from '../theme';

describe('theme (F-032)', () => {
  beforeEach(() => {
    localStorage.clear();
    applyTheme('dark');
  });

  it('defaults to the dark theme when nothing is stored', () => {
    initTheme();

    expect(document.documentElement.dataset.theme).toBe('dark');
    expect(useTheme().theme.value).toBe('dark');
  });

  it('restores a stored light preference', () => {
    localStorage.setItem('routine-kade-theme', 'light');

    initTheme();

    expect(document.documentElement.dataset.theme).toBe('light');
  });

  it('applies and persists the toggled theme', () => {
    useTheme().toggleTheme();

    expect(document.documentElement.dataset.theme).toBe('light');
    expect(localStorage.getItem('routine-kade-theme')).toBe('light');

    useTheme().toggleTheme();

    expect(document.documentElement.dataset.theme).toBe('dark');
    expect(localStorage.getItem('routine-kade-theme')).toBe('dark');
  });
});
