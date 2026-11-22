import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

export type UserRole = 'user' | 'mentor' | 'admin';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  timezone: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isLoading: false,
  }),

  actions: {
    /** Authenticate with email/password, then load the canonical profile. */
    async login(email: string, password: string): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<{ message: string }>('/api/v1/auth/login', {
          method: 'POST',
          body: { email, password },
        });

        // Login only returns a message; the session cookie is the real state.
        this.user = await apiRequest<User>('/api/v1/auth/me', { method: 'GET' });
      } catch (error) {
        // A rejected login must not leave a stale identity behind.
        this.user = null;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    /** Revoke the session server-side, then forget the user locally. */
    async logout(): Promise<void> {
      try {
        await apiRequest<{ message: string }>('/api/v1/auth/logout', {
          method: 'POST',
        });
      } finally {
        // The local session ends even if the server is unreachable.
        this.user = null;
      }
    },

    /** Persist a new IANA timezone and mirror the value the server stored. */
    async updateTimezone(timezone: string): Promise<void> {
      const response = await apiRequest<{ message: string; timezone: string }>(
        '/api/v1/auth/me/timezone',
        { method: 'PUT', body: { timezone } },
      );

      if (this.user) {
        this.user.timezone = response.timezone;
      }
    },

    /** Hydrate the store from the HttpOnly session cookie on app boot. */
    async init(): Promise<void> {
      try {
        this.user = await apiRequest<User>('/api/v1/auth/me', { method: 'GET' });
      } catch {
        // No valid session (typically 401): the visitor is simply signed out.
        this.user = null;
      }
    },
  },
});
