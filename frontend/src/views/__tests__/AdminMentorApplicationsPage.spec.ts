import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import AdminMentorApplicationsPage from '../admin/AdminMentorApplicationsPage.vue';

const { applicationStore, fetchApplicationsMock, approveMock, rejectMock } = vi.hoisted(
  () => {
    const fetchApplicationsMock = vi.fn();
    const approveMock = vi.fn();
    const rejectMock = vi.fn();

    return {
      fetchApplicationsMock,
      approveMock,
      rejectMock,
      applicationStore: {
        applications: [] as {
          id: string;
          user_id: string;
          applicant_name: string;
          applicant_email: string;
          expertise: string;
          bio: string;
          documents: string | null;
          status: 'pending' | 'approved' | 'rejected';
          created_at: string;
          updated_at: string;
          reviewed_at: string | null;
        }[],
        isLoading: false,
        fetchApplications: fetchApplicationsMock,
        approve: approveMock,
        reject: rejectMock,
      },
    };
  },
);

vi.mock('@/stores/mentorApplication', () => ({
  useMentorApplicationStore: () => applicationStore,
  applicationStatusLabels: {
    pending: 'در انتظار تایید',
    approved: 'تایید شده',
    rejected: 'رد شده',
  },
}));

const APPLICATION = {
  id: 'application-id',
  user_id: 'user-id',
  applicant_name: 'سارا احمدی',
  applicant_email: 'sara@example.com',
  expertise: 'برنامه‌ریزی درسی',
  bio: 'ده سال تجربه مشاوره تحصیلی.',
  documents: 'https://example.com/certificate',
  status: 'pending' as const,
  created_at: '2026-11-26T08:00:00Z',
  updated_at: '2026-11-26T08:00:00Z',
  reviewed_at: null,
};

function mountPage() {
  return mount(AdminMentorApplicationsPage);
}

function button(wrapper: ReturnType<typeof mount>, text: string) {
  return wrapper.findAll('button').find((candidate) => candidate.text() === text);
}

describe('AdminMentorApplicationsPage (F-036)', () => {
  beforeEach(() => {
    fetchApplicationsMock.mockReset().mockResolvedValue(undefined);
    approveMock.mockReset().mockResolvedValue(undefined);
    rejectMock.mockReset().mockResolvedValue(undefined);
    applicationStore.applications = [];
    applicationStore.isLoading = false;
  });

  it('shows an empty state when nothing awaits review', async () => {
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain('درخواستی در انتظار بررسی وجود ندارد.');
    expect(fetchApplicationsMock).toHaveBeenCalledTimes(1);
  });

  it('renders the applicant details and approves the request', async () => {
    applicationStore.applications = [{ ...APPLICATION }];
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain('سارا احمدی');
    expect(wrapper.text()).toContain('sara@example.com');
    expect(wrapper.text()).toContain('برنامه‌ریزی درسی');
    expect(wrapper.text()).toContain('در انتظار تایید');

    await button(wrapper, 'تایید')?.trigger('click');
    await flushPromises();

    expect(approveMock).toHaveBeenCalledWith('application-id');
  });

  it('rejects the request', async () => {
    applicationStore.applications = [{ ...APPLICATION }];
    const wrapper = mountPage();
    await flushPromises();

    await button(wrapper, 'رد درخواست')?.trigger('click');
    await flushPromises();

    expect(rejectMock).toHaveBeenCalledWith('application-id');
  });

  it('hides the review controls once a request is reviewed', async () => {
    applicationStore.applications = [{ ...APPLICATION, status: 'approved' }];
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain('تایید شده');
    expect(button(wrapper, 'تایید')).toBeUndefined();
    expect(button(wrapper, 'رد درخواست')).toBeUndefined();
  });
});
