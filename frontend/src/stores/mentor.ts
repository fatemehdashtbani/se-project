import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

export type ProgramCategory = 'study' | 'sport' | 'life' | 'other';

export interface Mentor {
  id: string;
  name: string;
  headline: string | null;
  bio: string | null;
}

export interface MentorClient {
  id: string;
  name: string;
}

export interface MentorMessage {
  id: string;
  body: string;
  sender_id: string;
  created_at: string;
}

export interface MentorProgram {
  id: string;
  mentor_id: string;
  title: string;
  description: string | null;
  category: ProgramCategory;
  routine_id: string | null;
  created_at: string;
}

interface MentorListResponse {
  items: Mentor[];
  total: number;
}

interface SelectedMentorResponse {
  mentor: Mentor | null;
}

interface MentorClientListResponse {
  items: MentorClient[];
  total: number;
}

interface MentorMessageListResponse {
  items: MentorMessage[];
  total: number;
}

interface MentorProgramListResponse {
  items: MentorProgram[];
  total: number;
}

interface MessageQuery {
  mentorId?: string;
  clientId?: string;
}

interface ProgramQuery {
  clientId?: string;
}

function normalizeMessageQuery(
  first?: string | MessageQuery,
  second?: string,
): MessageQuery {
  if (typeof first === 'string') {
    return { mentorId: first, clientId: second };
  }
  return first ?? {};
}

function normalizeProgramQuery(first?: string | ProgramQuery): ProgramQuery {
  if (typeof first === 'string') {
    return { clientId: first };
  }
  return first ?? {};
}

export const useMentorStore = defineStore('mentor', {
  state: () => ({
    mentors: [] as Mentor[],
    selectedMentor: null as Mentor | null,
    messages: [] as MentorMessage[],
    programs: [] as MentorProgram[],
    clients: [] as MentorClient[],
    isLoading: false,
  }),

  actions: {
    async fetchMentors(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<MentorListResponse>('/api/v1/mentors', {
          method: 'GET',
        });
        this.mentors = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchSelectedMentor(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<SelectedMentorResponse>(
          '/api/v1/mentors/selected',
          { method: 'GET' },
        );
        this.selectedMentor = response.mentor;
      } finally {
        this.isLoading = false;
      }
    },

    async selectMentor(mentorId: string): Promise<Mentor> {
      this.isLoading = true;
      try {
        const mentor = await apiRequest<Mentor>('/api/v1/mentors/selected', {
          method: 'PUT',
          body: { mentor_id: mentorId },
        });
        this.selectedMentor = mentor;
        return mentor;
      } finally {
        this.isLoading = false;
      }
    },

    async clearMentor(): Promise<void> {
      this.isLoading = true;
      try {
        await apiRequest<void>('/api/v1/mentors/selected', { method: 'DELETE' });
        this.selectedMentor = null;
        this.messages = [];
        this.programs = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchMessages(
      first?: string | MessageQuery,
      second?: string,
    ): Promise<void> {
      const { mentorId, clientId } = normalizeMessageQuery(first, second);
      const params = new URLSearchParams();
      if (mentorId) params.set('mentor_id', mentorId);
      if (clientId) params.set('client_id', clientId);
      const query = params.toString();
      const path = query
        ? `/api/v1/mentor-messages?${query}`
        : '/api/v1/mentor-messages';

      this.isLoading = true;
      try {
        const response = await apiRequest<MentorMessageListResponse>(path, {
          method: 'GET',
        });
        this.messages = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async sendMessage(
      bodyOrPayload:
        | string
        | { body: string; mentorId?: string; clientId?: string; mentor_id?: string; client_id?: string },
      mentorId?: string,
      clientId?: string,
    ): Promise<MentorMessage> {
      let body: string;
      let mId: string | undefined;
      let cId: string | undefined;

      if (typeof bodyOrPayload === 'string') {
        body = bodyOrPayload;
        mId = mentorId;
        cId = clientId;
      } else {
        body = bodyOrPayload.body;
        mId = bodyOrPayload.mentorId ?? bodyOrPayload.mentor_id ?? mentorId;
        cId = bodyOrPayload.clientId ?? bodyOrPayload.client_id ?? clientId;
      }

      this.isLoading = true;
      try {
        const message = await apiRequest<MentorMessage>('/api/v1/mentor-messages', {
          method: 'POST',
          body: {
            mentor_id: mId,
            client_id: cId,
            body,
          },
        });
        this.messages = [...this.messages, message];
        return message;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchPrograms(first?: string | ProgramQuery): Promise<void> {
      const { clientId } = normalizeProgramQuery(first);
      const path = clientId
        ? `/api/v1/mentor-programs?client_id=${encodeURIComponent(clientId)}`
        : '/api/v1/mentor-programs';

      this.isLoading = true;
      try {
        const response = await apiRequest<MentorProgramListResponse>(path, {
          method: 'GET',
        });
        this.programs = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async adoptProgram(programId: string): Promise<MentorProgram> {
      this.isLoading = true;
      try {
        const program = await apiRequest<MentorProgram>(
          `/api/v1/mentor-programs/${programId}/adopt`,
          { method: 'POST' },
        );
        this.programs = this.programs.map((item) =>
          item.id === programId ? program : item,
        );
        return program;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchClients(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<MentorClientListResponse>(
          '/api/v1/mentors/me/clients',
          { method: 'GET' },
        );
        this.clients = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async sendProgram(payload: {
      clientId: string;
      client_id?: string;
      title: string;
      description?: string | null;
      category: ProgramCategory;
    }): Promise<MentorProgram> {
      this.isLoading = true;
      try {
        const program = await apiRequest<MentorProgram>('/api/v1/mentor-programs', {
          method: 'POST',
          body: {
            client_id: payload.clientId ?? payload.client_id,
            title: payload.title,
            description: payload.description ?? null,
            category: payload.category,
          },
        });
        this.programs = [program, ...this.programs];
        return program;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
