import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

export interface User {
  id: string;
  email: string;
  role: string;
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
      await apiRequest<{ message: string }>('/api/v1/auth/logout', {
        method: 'POST',
      });

      this.user = null;
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
