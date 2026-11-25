import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

/** A note returned by the API (F-033). */
export interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

interface NoteListResponse {
  items: Note[];
  total: number;
}

export const useNoteStore = defineStore('notes', {
  state: () => ({
    notes: [] as Note[],
    isLoading: false,
  }),

  actions: {
    /** Load the caller's notes, most recently edited first. */
    async fetchNotes(): Promise<void> {
      this.isLoading = true;

      try {
        const response = await apiRequest<NoteListResponse>('/api/v1/notes', { method: 'GET' });
        this.notes = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    /** Create a note and append the server's representation. */
    async createNote(title: string, content: string): Promise<void> {
      this.isLoading = true;

      try {
        const note = await apiRequest<Note>('/api/v1/notes', {
          method: 'POST',
          body: { title, content },
        });
        this.notes = [note, ...this.notes];
      } finally {
        this.isLoading = false;
      }
    },

    /** Apply an edit and mirror the server's representation. */
    async updateNote(id: string, title: string, content: string): Promise<void> {
      this.isLoading = true;

      try {
        const note = await apiRequest<Note>(`/api/v1/notes/${id}`, {
          method: 'PUT',
          body: { title, content },
        });
        this.notes = this.notes.map((entry) => (entry.id === id ? note : entry));
      } finally {
        this.isLoading = false;
      }
    },

    /** Remove a note after the server accepted the delete. */
    async deleteNote(id: string): Promise<void> {
      this.isLoading = true;

      try {
        await apiRequest<void>(`/api/v1/notes/${id}`, { method: 'DELETE' });
        this.notes = this.notes.filter((note) => note.id !== id);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
