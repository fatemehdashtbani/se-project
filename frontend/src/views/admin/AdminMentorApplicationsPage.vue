<template>
  <section>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-xl font-bold text-white">درخواست‌های مربیگری</h2>
        <p class="mt-1 text-sm text-slate-400">
          درخواست‌های کاربران را بررسی کنید. با تایید، نقش حساب به مربی تغییر می‌کند.
        </p>
      </div>
      <span class="rounded-lg bg-slate-800 px-3 py-1 text-sm text-slate-300">
        {{ mentorApplicationStore.applications.length }} درخواست
      </span>
    </div>

    <p
      v-if="errorMessage"
      role="alert"
      class="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
    >
      {{ errorMessage }}
    </p>

    <p v-if="mentorApplicationStore.isLoading" class="mt-6 text-sm text-slate-400">
      در حال بارگذاری...
    </p>

    <p
      v-else-if="mentorApplicationStore.applications.length === 0"
      class="mt-6 rounded-2xl border border-slate-800 bg-slate-900/60 px-6 py-10 text-center text-sm text-slate-400"
    >
      درخواستی در انتظار بررسی وجود ندارد.
    </p>

    <ul v-else class="mt-6 space-y-4">
      <li
        v-for="application in mentorApplicationStore.applications"
        :key="application.id"
        class="rounded-2xl border border-slate-800 bg-slate-900/70 p-5"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 class="font-semibold text-white">{{ application.applicant_name }}</h3>
            <p dir="ltr" class="mt-1 text-left text-xs text-slate-500">
              {{ application.applicant_email }}
            </p>
          </div>
          <span
            class="rounded-md px-2 py-1 text-xs font-medium"
            :class="statusClass(application.status)"
          >
            {{ applicationStatusLabels[application.status] }}
          </span>
        </div>

        <dl class="mt-4 space-y-2 text-sm">
          <div>
            <dt class="font-medium text-slate-300">حوزه تخصص</dt>
            <dd class="mt-0.5 text-slate-400">{{ application.expertise }}</dd>
          </div>
          <div>
            <dt class="font-medium text-slate-300">بیوگرافی</dt>
            <dd class="mt-0.5 whitespace-pre-line text-slate-400">{{ application.bio }}</dd>
          </div>
          <div v-if="application.documents">
            <dt class="font-medium text-slate-300">مدارک و سوابق</dt>
            <dd class="mt-0.5 whitespace-pre-line break-words text-slate-400">
              {{ application.documents }}
            </dd>
          </div>
          <div>
            <dt class="font-medium text-slate-300">تاریخ درخواست</dt>
            <dd class="mt-0.5 text-slate-400">{{ formatDate(application.created_at) }}</dd>
          </div>
        </dl>

        <div v-if="application.status === 'pending'" class="mt-4 flex gap-2">
          <button
            type="button"
            class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400/70 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="mentorApplicationStore.isLoading"
            @click="handleApprove(application.id)"
          >
            تایید
          </button>
          <button
            type="button"
            class="rounded-md border border-red-500/50 px-4 py-2 text-sm font-medium text-red-300 transition-colors hover:bg-red-500/10 focus:outline-none focus:ring-2 focus:ring-red-400/60 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="mentorApplicationStore.isLoading"
            @click="handleReject(application.id)"
          >
            رد درخواست
          </button>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import {
  applicationStatusLabels,
  useMentorApplicationStore,
  type MentorApplicationStatus,
} from '@/stores/mentorApplication';

const mentorApplicationStore = useMentorApplicationStore();
const errorMessage = ref('');

function statusClass(status: MentorApplicationStatus): string {
  switch (status) {
    case 'approved':
      return 'bg-emerald-500/10 text-emerald-300';
    case 'rejected':
      return 'bg-red-500/10 text-red-300';
    default:
      return 'bg-amber-500/10 text-amber-300';
  }
}

function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleDateString('fa-IR');
  } catch {
    return value;
  }
}

async function loadApplications(): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorApplicationStore.fetchApplications();
  } catch {
    errorMessage.value = 'بارگذاری درخواست‌ها ناموفق بود.';
  }
}

async function handleApprove(applicationId: string): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorApplicationStore.approve(applicationId);
  } catch {
    errorMessage.value = 'تایید درخواست ناموفق بود.';
  }
}

async function handleReject(applicationId: string): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorApplicationStore.reject(applicationId);
  } catch {
    errorMessage.value = 'رد درخواست ناموفق بود.';
  }
}

onMounted(() => {
  void loadApplications();
});
</script>
