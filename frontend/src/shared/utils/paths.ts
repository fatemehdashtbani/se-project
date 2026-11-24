import type { UserRole } from '@/stores/auth';

/** Landing page for a freshly authenticated session (F-030). */
export function panelPath(role: UserRole | null | undefined): string {
  return role === 'admin' ? '/admin' : '/dashboard';
}

/** Persian labels for the server-owned roles. */
export const roleLabels: Record<UserRole, string> = {
  user: 'کاربر',
  mentor: 'منتور',
  admin: 'مدیر سامانه',
};
