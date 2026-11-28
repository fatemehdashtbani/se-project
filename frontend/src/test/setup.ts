/**
 * Node 26 defines its own `localStorage` global, which is unusable without the
 * `--localstorage-file` flag. Vitest's jsdom environment copies jsdom's window
 * keys onto globalThis but skips names that already exist, so `localStorage`
 * stays as the unusable Node property and component tests cannot read or clear
 * it. Install a small in-memory Storage implementation for tests only.
 */
class MemoryStorage {
  private readonly items = new Map<string, string>();

  get length(): number {
    return this.items.size;
  }

  clear(): void {
    this.items.clear();
  }

  getItem(key: string): string | null {
    return this.items.has(key) ? (this.items.get(key) as string) : null;
  }

  key(index: number): string | null {
    return Array.from(this.items.keys())[index] ?? null;
  }

  removeItem(key: string): void {
    this.items.delete(key);
  }

  setItem(key: string, value: string): void {
    this.items.set(key, String(value));
  }
}

for (const key of ['localStorage', 'sessionStorage'] as const) {
  if (!globalThis[key]) {
    Object.defineProperty(globalThis, key, {
      value: new MemoryStorage() as unknown as Storage,
      configurable: true,
      writable: true,
    });
  }
}
