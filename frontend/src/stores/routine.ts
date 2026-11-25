import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

/** Public routine representation returned by the API (F-005). */
export interface Routine {
  id: string;
  title: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface RoutineListResponse {
  items: Routine[];
  total: number;
}

export const useRoutineStore = defineStore('routine', {
  state: () => ({
    routines: [] as Routine[],
    isLoading: false,
  }),

  actions: {
    /** Load the caller's active routines into the store. */
    async fetchRoutines(): Promise<void> {
      this.isLoading = true;

      try {
        const response = await apiRequest<RoutineListResponse>('/api/v1/routines', {
          method: 'GET',
        });
        this.routines = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    /** Create a routine and append the server's representation to the list. */
    async createRoutine(title: string, description: string | null = null): Promise<void> {
      this.isLoading = true;

      try {
        const routine = await apiRequest<Routine>('/api/v1/routines', {
          method: 'POST',
          body: { title, description },
        });
        this.routines.push(routine);
      } finally {
        this.isLoading = false;
      }
    },

    /** Apply an edit and mirror the server's representation in the list. */
    async updateRoutine(
      id: string,
      title: string,
      description: string | null = null,
    ): Promise<void> {
      this.isLoading = true;

      try {
        const routine = await apiRequest<Routine>(`/api/v1/routines/${id}`, {
          method: 'PUT',
          body: { title, description },
        });
        this.routines = this.routines.map((item) => (item.id === id ? routine : item));
      } finally {
        this.isLoading = false;
      }
    },

    /** Remove a routine from the list after the server accepted the delete. */
    async deleteRoutine(id: string): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<void>(`/api/v1/routines/${id}`, { method: 'DELETE' });
        this.routines = this.routines.filter((routine) => routine.id !== id);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
