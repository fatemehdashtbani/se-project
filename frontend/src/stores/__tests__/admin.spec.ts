import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';

const { apiRequest } = vi.hoisted(() => ({ apiRequest: vi.fn() }));

vi.mock('@/shared/api/client', () => ({ apiRequest }));

import { useAdminStore } from '../admin';

describe('admin store (F-037)', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiRequest.mockReset();
  });

  it('maps the user filters onto the page query', async () => {
    apiRequest.mockResolvedValue({ items: [], total: 0 });
    const store = useAdminStore();

    await store.fetchUsers({ search: 'sara', role: 'mentor', status: 'active', limit: 10, offset: 20 });

    expect(apiRequest).toHaveBeenCalledWith(
      '/api/v1/admin/users?search=sara&role=mentor&status=active&limit=10&offset=20',
    );
  });

  it('posts the flag when an account is banned or re-enabled', async () => {
    apiRequest.mockResolvedValue({});
    const store = useAdminStore();

    await store.setUserBanned('user-1', true);
    await store.setUserActive('user-1', false);

    expect(apiRequest).toHaveBeenNthCalledWith(1, '/api/v1/admin/users/user-1/ban', {
      method: 'POST',
      body: { value: true },
    });
    expect(apiRequest).toHaveBeenNthCalledWith(
      2,
      '/api/v1/admin/users/user-1/activation',
      { method: 'POST', body: { value: false } },
    );
  });

  it('returns the temporary password from a reset', async () => {
    apiRequest.mockResolvedValue({ temporary_password: 'temp-secret' });
    const store = useAdminStore();

    await expect(store.resetUserPassword('user-1')).resolves.toBe('temp-secret');
  });

  it('stores dashboard counters returned by the API', async () => {
    const dashboard = { total_users: 3, activity: [] };
    apiRequest.mockResolvedValue(dashboard);
    const store = useAdminStore();

    await store.fetchDashboard();

    expect(store.dashboard).toStrictEqual(dashboard);
    expect(apiRequest).toHaveBeenCalledWith('/api/v1/admin/dashboard');
  });

  it('sends templates and categories through the admin endpoints', async () => {
    apiRequest.mockResolvedValue({});
    const store = useAdminStore();

    await store.createTemplate({
      title: 'روتین مطالعه',
      description: null,
      category: 'تحصیلی',
      duration_days: 30,
      is_published: true,
    });
    await store.updateCategory('cat-1', {
      name: 'ورزشی',
      description: null,
      color: '#7c3aed',
    });

    expect(apiRequest).toHaveBeenNthCalledWith(1, '/api/v1/admin/templates', {
      method: 'POST',
      body: {
        title: 'روتین مطالعه',
        description: null,
        category: 'تحصیلی',
        duration_days: 30,
        is_published: true,
      },
    });
    expect(apiRequest).toHaveBeenNthCalledWith(2, '/api/v1/admin/categories/cat-1', {
      method: 'PUT',
      body: { name: 'ورزشی', description: null, color: '#7c3aed' },
    });
  });
});
