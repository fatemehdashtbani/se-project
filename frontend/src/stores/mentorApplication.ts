import { defineStore } from 'pinia';
import { apiRequest } from '@/shared/api/client';

export type MentorApplicationStatus = 'pending' | 'approved' | 'rejected';

export interface MentorApplication {
  id: string;
  user_id: string;
  expertise: string;
  bio: string;
  documents: string | null;
  status: MentorApplicationStatus;
  created_at: string;
  updated_at: string;
  reviewed_at: string | null;
}

/** An application as it appears in the administrator's review queue. */
export interface AdminMentorApplication extends MentorApplication {
  applicant_name: string;
  applicant_email: string;
}

export interface MentorApplicationPayload {
  expertise: string;
  bio: string;
  documents: string | null;
}

interface MyApplicationResponse {
  application: MentorApplication | null;
}

interface ApplicationListResponse {
  items: AdminMentorApplication[];
  total: number;
}

/** Persian labels for the review states of one application. */
export const applicationStatusLabels: Record<MentorApplicationStatus, string> = {
  pending: 'در انتظار تایید',
  approved: 'تایید شده',
  rejected: 'رد شده',
};

export const useMentorApplicationStore = defineStore('mentorApplication', {
  state: () => ({
    application: null as MentorApplication | null,
    applications: [] as AdminMentorApplication[],
    isLoading: false,
  }),

  actions: {
    /** Read the caller's own application, whatever its state. */
    async fetchMine(): Promise<void> {
      this.isLoading = true;
      try {
        const response = await apiRequest<MyApplicationResponse>(
          '/api/v1/mentor-applications/me',
          { method: 'GET' },
        );
        this.application = response.application;
      } finally {
        this.isLoading = false;
      }
    },

    /** Submit or resubmit the application; it always returns to pending. */
    async submit(payload: MentorApplicationPayload): Promise<MentorApplication> {
      this.isLoading = true;
      try {
        const application = await apiRequest<MentorApplication>(
          '/api/v1/mentor-applications',
          {
            method: 'POST',
            body: {
              expertise: payload.expertise,
              bio: payload.bio,
              documents: payload.documents,
            },
          },
        );
        this.application = application;
        return application;
      } finally {
        this.isLoading = false;
      }
    },

    /** Admin queue, optionally narrowed to one review state. */
    async fetchApplications(status?: MentorApplicationStatus): Promise<void> {
      const path = status
        ? `/api/v1/admin/mentor-applications?status=${status}`
        : '/api/v1/admin/mentor-applications';

      this.isLoading = true;
      try {
        const response = await apiRequest<ApplicationListResponse>(path, {
          method: 'GET',
        });
        this.applications = response.items;
      } finally {
        this.isLoading = false;
      }
    },

    async approve(applicationId: string): Promise<MentorApplication> {
      this.isLoading = true;
      try {
        const updated = await apiRequest<MentorApplication>(
          `/api/v1/admin/mentor-applications/${applicationId}/approve`,
          { method: 'POST' },
        );
        this.replace(updated);
        return updated;
      } finally {
        this.isLoading = false;
      }
    },

    async reject(applicationId: string): Promise<MentorApplication> {
      this.isLoading = true;
      try {
        const updated = await apiRequest<MentorApplication>(
          `/api/v1/admin/mentor-applications/${applicationId}/reject`,
          { method: 'POST' },
        );
        this.replace(updated);
        return updated;
      } finally {
        this.isLoading = false;
      }
    },

    /** Keep the applicant identity the review response does not repeat. */
    replace(updated: MentorApplication): void {
      this.applications = this.applications.map((item) =>
        item.id === updated.id ? { ...item, ...updated } : item,
      );
    },
  },
});
