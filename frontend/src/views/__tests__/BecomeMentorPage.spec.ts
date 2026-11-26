import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils';
import BecomeMentorPage from '../BecomeMentorPage.vue';

const { authStore, applicationStore, fetchMineMock, submitMock } = vi.hoisted(() => {
  const fetchMineMock = vi.fn();
  const submitMock = vi.fn();

  return {
    fetchMineMock,
    submitMock,
    authStore: {
      user: {
        id: 'user-id',
        email: 'user@example.com',
        role: 'user' as 'user' | 'mentor' | 'admin',
        timezone: 'UTC',
        username: 'sara',
        first_name: 'سارا',
        last_name: null,
        phone_number: null,
      },
      isLoading: false,
    },
    applicationStore: {
      application: null as {
        id: string;
        user_id: string;
        expertise: string;
        bio: string;
        documents: string | null;
        status: 'pending' | 'approved' | 'rejected';
        created_at: string;
        updated_at: string;
        reviewed_at: string | null;
      } | null,
      isLoading: false,
      fetchMine: fetchMineMock,
      submit: submitMock,
    },
  };
});

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}));

vi.mock('@/stores/mentorApplication', () => ({
  useMentorApplicationStore: () => applicationStore,
}));

const APPLICATION = {
  id: 'application-id',
  user_id: 'user-id',
  expertise: 'برنامه‌ریزی درسی',
  bio: 'ده سال تجربه مشاوره تحصیلی.',
  documents: 'https://example.com/certificate',
  status: 'pending' as const,
  created_at: '2026-11-26T08:00:00Z',
  updated_at: '2026-11-26T08:00:00Z',
  reviewed_at: null,
};

function mountPage() {
  return mount(BecomeMentorPage, {
    global: {
      stubs: {
        RouterLink: RouterLinkStub,
        BottomNav: { template: '<div />' },
      },
    },
  });
}

describe('BecomeMentorPage (F-036)', () => {
  beforeEach(() => {
    fetchMineMock.mockReset().mockResolvedValue(undefined);
    submitMock.mockReset().mockResolvedValue(APPLICATION);
    applicationStore.application = null;
    applicationStore.isLoading = false;
    authStore.user = { ...authStore.user, role: 'user' };
  });

  it('renders the expertise, biography and documents fields', async () => {
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.get('label[for="expertise"]').text()).toBe('حوزه تخصص');
    expect(wrapper.get('label[for="bio"]').text()).toBe('بیوگرافی');
    expect(wrapper.get('label[for="documents"]').text()).toBe('مدارک و سوابق');
    expect(wrapper.get('button[type="submit"]').text()).toBe('ارسال درخواست');
    expect(fetchMineMock).toHaveBeenCalledTimes(1);
  });

  it('submits trimmed details and reports the pending status', async () => {
    const wrapper = mountPage();
    await flushPromises();

    await wrapper.get('#expertise').setValue('  برنامه‌ریزی درسی  ');
    await wrapper.get('#bio').setValue('  ده سال تجربه مشاوره تحصیلی.  ');
    await wrapper.get('#documents').setValue('   ');
    await wrapper.get('form').trigger('submit.prevent');
    await flushPromises();

    expect(submitMock).toHaveBeenCalledWith({
      expertise: 'برنامه‌ریزی درسی',
      bio: 'ده سال تجربه مشاوره تحصیلی.',
      documents: null,
    });
    expect(wrapper.text()).toContain('درخواست شما ثبت شد و در انتظار تایید مدیر است.');
  });

  it('rejects an empty form without calling the store', async () => {
    const wrapper = mountPage();
    await flushPromises();

    await wrapper.get('form').trigger('submit.prevent');
    await flushPromises();

    expect(submitMock).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain('حوزه تخصص الزامی است.');
    expect(wrapper.text()).toContain('بیوگرافی الزامی است.');
  });

  it('shows the pending request instead of the form', async () => {
    applicationStore.application = { ...APPLICATION };
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain('درخواست شما در انتظار تایید است');
    expect(wrapper.find('#expertise').exists()).toBe(false);
  });

  it('offers a prefilled form again after a rejection', async () => {
    applicationStore.application = { ...APPLICATION, status: 'rejected' };
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain('درخواست قبلی شما تایید نشد');
    expect((wrapper.get('#expertise').element as HTMLInputElement).value).toBe(
      'برنامه‌ریزی درسی',
    );
    expect(wrapper.get('#bio').element).toHaveProperty(
      'value',
      'ده سال تجربه مشاوره تحصیلی.',
    );
  });

  it('tells an existing mentor that no request is needed', async () => {
    authStore.user = { ...authStore.user, role: 'mentor' };
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain('شما مربی هستید');
    expect(wrapper.find('form').exists()).toBe(false);
    const link = wrapper.findAllComponents(RouterLinkStub).find((item) => item.text() === 'میز کار مربی');
    expect(link?.props('to')).toBe('/mentor');
  });
});
