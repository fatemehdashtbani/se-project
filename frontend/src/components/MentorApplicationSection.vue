<template>
  <section class="mt-10 rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="min-w-0">
        <h2 class="text-xl font-semibold text-white">همکاری به عنوان مربی</h2>
        <p class="mt-2 text-sm text-slate-400">
          اگر در حوزه‌ای تخصص دارید، درخواست همکاری بفرستید تا پس از تایید مدیر به عنوان مربی
          فعالیت کنید.
        </p>
        <p v-if="applicationState" class="mt-2 text-sm" :class="applicationState.tone">
          {{ applicationState.message }}
        </p>
      </div>
      <RouterLink
        to="/become-a-mentor"
        class="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
      >
        درخواست همکاری به عنوان مربی
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useMentorApplicationStore } from '@/stores/mentorApplication';

const mentorApplicationStore = useMentorApplicationStore();

const applicationState = computed(() => {
  switch (mentorApplicationStore.application?.status) {
    case 'pending':
      return { message: 'درخواست شما در انتظار تایید مدیر است.', tone: 'text-amber-300' };
    case 'rejected':
      return {
        message: 'درخواست شما رد شده است؛ می‌توانید اطلاعات را اصلاح و دوباره ارسال کنید.',
        tone: 'text-rose-300',
      };
    case 'approved':
      return { message: 'درخواست شما تایید شده است.', tone: 'text-emerald-300' };
    default:
      return null;
  }
});

onMounted(async () => {
  try {
    await mentorApplicationStore.fetchMine();
  } catch {
    // The dashboard stays usable when the application status is unavailable.
  }
});
</script>
