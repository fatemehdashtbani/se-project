import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

/** A dated calendar entry returned by the API (F-033). */
export interface CalendarEvent {
  id: string;
  title: string;
  event_date: string;
  /** Local wall-clock time (`HH:MM:SS`), or null for a day-only event (F-034). */
  event_time: string | null;
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

    /** Create an event for one day, optionally at one time, and append it. */
    async createEvent(title: string, eventDate: string, eventTime?: string | null): Promise<void> {
      this.isLoading = true;

      try {
        const body: Record<string, unknown> = { title, event_date: eventDate };
        if (eventTime) {
          body.event_time = eventTime;
        }

        const event = await apiRequest<CalendarEvent>('/api/v1/calendar-events', {
          method: 'POST',
          body,
        });
        this.events = [...this.events, event].sort((a, b) =>
          a.event_date.localeCompare(b.event_date) ||
          (a.event_time ?? '').localeCompare(b.event_time ?? ''),
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
