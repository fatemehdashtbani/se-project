import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

/** A dated calendar entry returned by the API (F-033). */
export interface CalendarEvent {
  id: string;
  title: string;
  event_date: string;
  created_at: string;
}

interface CalendarEventListResponse {
  items: CalendarEvent[];
  total: number;
}

export const useCalendarStore = defineStore('calendar', {
  state: () => ({
    events: [] as CalendarEvent[],
    isLoading: false,
  }),

  actions: {
    /** Load every event the caller owns; the page filters by month. */
    async fetchEvents(): Promise<void> {
      this.isLoading = true;

      try {
        const response = await apiRequest<CalendarEventListResponse>('/api/v1/calendar-events', {
          method: 'GET',
        });
        this.events = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    /** Create an event for one day and append the server's representation. */
    async createEvent(title: string, eventDate: string): Promise<void> {
      this.isLoading = true;

      try {
        const event = await apiRequest<CalendarEvent>('/api/v1/calendar-events', {
          method: 'POST',
          body: { title, event_date: eventDate },
        });
        this.events = [...this.events, event].sort((a, b) =>
          a.event_date.localeCompare(b.event_date),
        );
      } finally {
        this.isLoading = false;
      }
    },

    /** Remove an event after the server accepted the delete. */
    async deleteEvent(id: string): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<void>(`/api/v1/calendar-events/${id}`, { method: 'DELETE' });
        this.events = this.events.filter((event) => event.id !== id);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
