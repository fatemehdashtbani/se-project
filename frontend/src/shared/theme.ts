import { computed, ref, type ComputedRef, type Ref } from 'vue';

export type Theme = 'dark' | 'light';

const STORAGE_KEY = 'routine-kade-theme';

const theme = ref<Theme>('dark');

function isTheme(value: string | null): value is Theme {
  return value === 'dark' || value === 'light';
}

/** Apply a theme to the document and remember the visitor's choice. */
export function applyTheme(next: Theme): void {
  theme.value = next;
  document.documentElement.dataset.theme = next;

  try {
    localStorage.setItem(STORAGE_KEY, next);
  } catch {
    // Private mode or blocked storage: the theme still applies for this visit.
  }
}

/** Read the persisted theme (default: dark) before the first render. */
export function initTheme(): void {
  let stored: string | null = null;

  try {
    stored = localStorage.getItem(STORAGE_KEY);
  } catch {
    stored = null;
  }

  applyTheme(isTheme(stored) ? stored : 'dark');
}

export function useTheme(): {
  theme: Ref<Theme>;
  isDark: ComputedRef<boolean>;
  toggleTheme: () => void;
} {
  return {
    theme,
    isDark: computed(() => theme.value === 'dark'),
    toggleTheme: () => applyTheme(theme.value === 'dark' ? 'light' : 'dark'),
  };
}
