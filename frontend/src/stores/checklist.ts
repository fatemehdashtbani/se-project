import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

/** One line of the personal checklist returned by the API (F-033). */
export interface ChecklistItem {
  id: string;
  title: string;
  is_done: boolean;
  created_at: string;
  updated_at: string;
}

interface ChecklistListResponse {
  items: ChecklistItem[];
  total: number;
  done: number;
}

export const useChecklistStore = defineStore('checklist', {
  state: () => ({
    items: [] as ChecklistItem[],
    isLoading: false,
  }),

  actions: {
    /** Load the caller's checklist. */
    async fetchItems(): Promise<void> {
      this.isLoading = true;

      try {
        const response = await apiRequest<ChecklistListResponse>('/api/v1/checklist-items', {
          method: 'GET',
        });
        this.items = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    /** Append a new item using the server's representation. */
    async createItem(title: string): Promise<void> {
      this.isLoading = true;

      try {
        const item = await apiRequest<ChecklistItem>('/api/v1/checklist-items', {
          method: 'POST',
          body: { title },
        });
        this.items.push(item);
      } finally {
        this.isLoading = false;
      }
    },

    /** Tick or untick an item and mirror the server's answer. */
    async setDone(id: string, isDone: boolean): Promise<void> {
      this.isLoading = true;

      try {
        const item = await apiRequest<ChecklistItem>(`/api/v1/checklist-items/${id}`, {
          method: 'PUT',
          body: { is_done: isDone },
        });
        this.items = this.items.map((entry) => (entry.id === id ? item : entry));
      } finally {
        this.isLoading = false;
      }
    },

    /** Remove an item from the list after the server accepted the delete. */
    async deleteItem(id: string): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<void>(`/api/v1/checklist-items/${id}`, { method: 'DELETE' });
        this.items = this.items.filter((item) => item.id !== id);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
