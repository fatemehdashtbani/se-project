<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 px-4 py-12 text-slate-100">
    <div
      class="mx-auto w-full max-w-md rounded-2xl border border-slate-800 bg-slate-800/60 p-8 shadow-xl"
    >
      <header class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-white">پروفایل</h1>
        <p class="mt-2 text-sm text-slate-400">
          اطلاعات حساب و منطقه زمانی خود را مدیریت کنید.
        </p>
      </header>

      <p
        v-if="successMessage"
        role="status"
        class="mb-4 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200"
      >
        {{ successMessage }}
      </p>

      <p
        v-if="serverError"
        role="alert"
        class="mb-4 rounded-lg border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-200"
      >
        {{ serverError }}
      </p>

      <dl class="mb-6 space-y-2">
        <div
          v-for="field in profileFields"
          :key="field.label"
          class="flex items-center justify-between gap-4 rounded-lg bg-slate-900/60 px-4 py-3"
        >
          <dt class="text-sm text-slate-400">{{ field.label }}</dt>
          <dd class="text-sm font-medium text-white" :dir="field.ltr ? 'ltr' : undefined">
            {{ field.value }}
          </dd>
        </div>
      </dl>

      <form class="space-y-5" novalidate @submit.prevent="handleSubmit">
        <div>
          <label for="timezone" class="mb-2 block text-sm font-medium text-slate-300">
            منطقه زمانی
          </label>
          <select
            id="timezone"
            v-model="selectedTimezone"
            dir="ltr"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          >
            <option v-for="zone in availableTimezones" :key="zone" :value="zone">
              {{ zone }}
            </option>
          </select>
          <p class="mt-1 text-xs text-slate-500">
            این منطقه برای تعیین «امروز» و محاسبه زنجیره عادت‌ها استفاده می‌شود.
          </p>
        </div>

        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full rounded-xl bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          ذخیره تغییرات
        </button>

        <button
          type="button"
          disabled
          title="به‌زودی"
          class="w-full cursor-not-allowed rounded-xl border border-slate-700 px-4 py-2.5 font-medium text-slate-500"
        >
          تغییر رمز عبور
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { useAuthStore } from '@/stores/auth';

const SUCCESS_MESSAGE = 'منطقه زمانی با موفقیت ذخیره شد';
const EMPTY_VALUE = '—';

/** Common IANA zones for the dropdown. The stored zone is injected if absent. */
const TIMEZONES = [
  'UTC',
  'Africa/Cairo',
  'Africa/Johannesburg',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/New_York',
  'America/Sao_Paulo',
  'Asia/Dubai',
  'Asia/Jerusalem',
  'Asia/Kolkata',
  'Asia/Riyadh',
  'Asia/Shanghai',
  'Asia/Singapore',
  'Asia/Tehran',
  'Asia/Tokyo',
  'Australia/Sydney',
  'Europe/Berlin',
  'Europe/Istanbul',
  'Europe/London',
  'Europe/Moscow',
  'Europe/Paris',
  'Pacific/Auckland',
] as const;

const authStore = useAuthStore();

const selectedTimezone = ref(authStore.user?.timezone ?? 'UTC');
const successMessage = ref('');
const serverError = ref('');
const isSubmitting = ref(false);

function display(value: string | null | undefined): string {
  return value && value.trim() !== '' ? value : EMPTY_VALUE;
}

const profileFields = computed(() => [
  { label: 'نام', value: display(authStore.user?.first_name) },
  { label: 'نام خانوادگی', value: display(authStore.user?.last_name) },
  { label: 'شماره تلفن', value: display(authStore.user?.phone_number), ltr: true },
  { label: 'ایمیل', value: display(authStore.user?.email), ltr: true },
]);

const availableTimezones = computed<string[]>(() => {
  const zones: string[] = [...TIMEZONES];
  const current = authStore.user?.timezone;

  // A stored zone outside the curated list must still be selectable, otherwise
  // the dropdown would silently fall back to its first option.
  if (current && !zones.includes(current)) {
    zones.unshift(current);
  }

  return zones;
});

async function handleSubmit(): Promise<void> {
  successMessage.value = '';
  serverError.value = '';
  isSubmitting.value = true;

  try {
    await authStore.updateTimezone(selectedTimezone.value);
    successMessage.value = SUCCESS_MESSAGE;
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  } finally {
    isSubmitting.value = false;
  }
}
</script>
