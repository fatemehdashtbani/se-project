import { describe, expect, it } from 'vitest';
import { panelPath, roleLabels } from '../paths';
import type { UserRole } from '@/stores/auth';

describe('panelPath (F-030)', () => {
  it('sends an admin to the admin panel', () => {
    expect(panelPath('admin')).toBe('/admin');
  });

  it('sends users, mentors and guests to the dashboard', () => {
    expect(panelPath('user')).toBe('/dashboard');
    expect(panelPath('mentor')).toBe('/dashboard');
    expect(panelPath(null)).toBe('/dashboard');
    expect(panelPath(undefined)).toBe('/dashboard');
  });

  it('provides Persian labels for every server role', () => {
    const roles: UserRole[] = ['user', 'mentor', 'admin'];

    expect(roles.map((role) => roleLabels[role])).toEqual([
      'کاربر',
      'منتور',
      'مدیر سامانه',
    ]);
  });
});
