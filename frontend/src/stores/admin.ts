/** Admin panel state and API calls (F-037). */

import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

export interface DailyActivityPoint {
  date: string;
  signups: number;
  routines: number;
  active_users: number;
}

export interface DashboardData {
  total_users: number;
  active_users: number;
  banned_users: number;
  total_routines: number;
  total_mentors: number;
  pending_mentor_requests: number;
  total_mentor_programs: number;
  active_mentorships: number;
  active_today: number;
  total_templates: number;
  total_categories: number;
  total_broadcasts: number;
  activity: DailyActivityPoint[];
}

export interface AdminUser {
  id: string;
  email: string;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  phone_number: string | null;
  role: 'user' | 'mentor' | 'admin';
  timezone: string;
  is_active: boolean;
  is_banned: boolean;
  created_at: string;
  routines_count: number;
}

export interface AdminMentor {
  id: string;
  name: string;
  email: string;
  headline: string | null;
  bio: string | null;
  clients_count: number;
  created_at: string;
}

export interface ConversationSummary {
  user_id: string;
  user_name: string;
  user_email: string;
  mentor_id: string;
  mentor_name: string;
  mentor_email: string;
  messages_count: number;
  last_message_at: string | null;
}

export interface AdminMessage {
  id: string;
  sender_id: string;
  sender_name: string;
  body: string;
  created_at: string;
}

export interface RoutineTemplate {
  id: string;
  title: string;
  description: string | null;
  category: string | null;
  duration_days: number | null;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface TemplatePayload {
  title: string;
  description: string | null;
  category: string | null;
  duration_days: number | null;
  is_published: boolean;
}

export interface HabitCategory {
  id: string;
  name: string;
  description: string | null;
  color: string;
  created_at: string;
}

export interface CategoryPayload {
  name: string;
  description: string | null;
  color: string;
}

export interface Broadcast {
  id: string;
  title: string;
  body: string;
  audience: string;
  recipients: number;
  created_at: string;
}

export interface SystemLog {
  id: string;
  level: 'error' | 'warning' | 'info' | 'audit';
  event: string;
  message: string;
  status_code: number | null;
  method: string | null;
  path: string | null;
  created_at: string;
}

export interface UserFilters {
  search?: string;
  role?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

interface ConversationMessagesResponse {
  user_id: string;
  mentor_id: string;
  items: AdminMessage[];
}

export const useAdminStore = defineStore('admin', {
  state: () => ({
    isLoading: false,
    dashboard: null as DashboardData | null,
    users: [] as AdminUser[],
    usersTotal: 0,
    mentors: [] as AdminMentor[],
    conversations: [] as ConversationSummary[],
    templates: [] as RoutineTemplate[],
    categories: [] as HabitCategory[],
    broadcasts: [] as Broadcast[],
    logs: [] as SystemLog[],
    logsTotal: 0,
  }),

  actions: {
    async fetchDashboard(): Promise<void> {
      this.isLoading = true;
      try {
        this.dashboard = await apiRequest<DashboardData>('/api/v1/admin/dashboard');
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUsers(filters: UserFilters = {}): Promise<void> {
      const params = new URLSearchParams();
      if (filters.search) params.set('search', filters.search);
      if (filters.role) params.set('role', filters.role);
      if (filters.status) params.set('status', filters.status);
      params.set('limit', String(filters.limit ?? 20));
      params.set('offset', String(filters.offset ?? 0));

      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<AdminUser>>(
          `/api/v1/admin/users?${params.toString()}`,
        );
        this.users = response.items;
        this.usersTotal = response.total;
      } finally {
        this.isLoading = false;
      }
    },

    async setUserBanned(userId: string, value: boolean): Promise<void> {
      await apiRequest(`/api/v1/admin/users/${userId}/ban`, {
        method: 'POST',
        body: { value },
      });
    },

    async setUserActive(userId: string, value: boolean): Promise<void> {
      await apiRequest(`/api/v1/admin/users/${userId}/activation`, {
        method: 'POST',
        body: { value },
      });
    },

    async resetUserPassword(userId: string): Promise<string> {
      const response = await apiRequest<{ temporary_password: string }>(
        `/api/v1/admin/users/${userId}/reset-password`,
        { method: 'POST' },
      );
      return response.temporary_password;
    },

    async fetchMentors(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<AdminMentor>>(
          '/api/v1/admin/mentors',
        );
        this.mentors = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async removeMentor(mentorId: string): Promise<void> {
      await apiRequest(`/api/v1/admin/mentors/${mentorId}/remove`, { method: 'POST' });
    },

    async assignMentor(userId: string, mentorId: string): Promise<void> {
      await apiRequest('/api/v1/admin/mentors/assign', {
        method: 'POST',
        body: { user_id: userId, mentor_id: mentorId },
      });
    },

    async fetchConversations(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<ConversationSummary>>(
          '/api/v1/admin/conversations',
        );
        this.conversations = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchConversationMessages(
      userId: string,
      mentorId: string,
    ): Promise<AdminMessage[]> {
      const params = new URLSearchParams({ user_id: userId, mentor_id: mentorId });
      const response = await apiRequest<ConversationMessagesResponse>(
        `/api/v1/admin/conversations/messages?${params.toString()}`,
      );
      return response.items;
    },

    async fetchTemplates(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<RoutineTemplate>>(
          '/api/v1/admin/templates',
        );
        this.templates = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async createTemplate(payload: TemplatePayload): Promise<void> {
      await apiRequest('/api/v1/admin/templates', { method: 'POST', body: payload });
    },

    async updateTemplate(id: string, payload: TemplatePayload): Promise<void> {
      await apiRequest(`/api/v1/admin/templates/${id}`, { method: 'PUT', body: payload });
    },

    async deleteTemplate(id: string): Promise<void> {
      await apiRequest(`/api/v1/admin/templates/${id}`, { method: 'DELETE' });
    },

    async fetchCategories(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<HabitCategory>>(
          '/api/v1/admin/categories',
        );
        this.categories = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async createCategory(payload: CategoryPayload): Promise<void> {
      await apiRequest('/api/v1/admin/categories', { method: 'POST', body: payload });
    },

    async updateCategory(id: string, payload: CategoryPayload): Promise<void> {
      await apiRequest(`/api/v1/admin/categories/${id}`, { method: 'PUT', body: payload });
    },

    async deleteCategory(id: string): Promise<void> {
      await apiRequest(`/api/v1/admin/categories/${id}`, { method: 'DELETE' });
    },

    async fetchBroadcasts(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<Broadcast>>(
          '/api/v1/admin/broadcasts',
        );
        this.broadcasts = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async createBroadcast(title: string, body: string): Promise<void> {
      await apiRequest('/api/v1/admin/broadcasts', {
        method: 'POST',
        body: { title, body },
      });
    },

    async deleteBroadcast(id: string): Promise<void> {
      await apiRequest(`/api/v1/admin/broadcasts/${id}`, { method: 'DELETE' });
    },

    async fetchLogs(level = '', search = '', offset = 0, limit = 20): Promise<void> {
      const params = new URLSearchParams();
      if (level) params.set('level', level);
      if (search) params.set('search', search);
      params.set('limit', String(limit));
      params.set('offset', String(offset));

      this.isLoading = true;
      try {
        const response = await apiRequest<ListResponse<SystemLog>>(
          `/api/v1/admin/logs?${params.toString()}`,
        );
        this.logs = response.items;
        this.logsTotal = response.total;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
