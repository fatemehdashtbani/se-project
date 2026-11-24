import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

export type UserRole = 'user' | 'mentor' | 'admin';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  timezone: string;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  phone_number: string | null;
}

/** Registration form values, using the client's camelCase naming. */
export interface RegisterPayload {
  email: string;
  password: string;
  username: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isLoading: false,
  }),

  actions: {
    /** Authenticate with an email or phone identifier plus the password. */
    async login(identifier: string, password: string): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<{ message: string }>('/api/v1/auth/login', {
          method: 'POST',
          body: { identifier, password },
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

    /** Create an account, then immediately establish a session for it.
     *
     * The outer isLoading guard keeps the submit button disabled across the
     * register→login→me sequence instead of flickering in between calls.
     */
    async register(payload: RegisterPayload): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<unknown>('/api/v1/auth/register', {
          method: 'POST',
          body: {
            email: payload.email,
            password: payload.password,
            username: payload.username,
            first_name: payload.firstName,
            last_name: payload.lastName,
            phone_number: payload.phoneNumber,
          },
        });

        await this.login(payload.email, payload.password);
      } finally {
        this.isLoading = false;
      }
    },

    /** Request a password-reset link (backend mock until F-022). */
    async forgotPassword(email: string): Promise<void> {
      await apiRequest<{ message: string }>('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: { email },
      });
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
