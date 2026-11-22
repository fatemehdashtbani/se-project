<template>
  <div dir="rtl" class="min-h-full bg-gray-100 px-4 py-12">
    <div class="mx-auto w-full max-w-md rounded-xl bg-white p-8 shadow-md">
      <header class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-gray-900">پروفایل</h1>
        <p class="mt-2 text-sm text-gray-500">اطلاعات حساب و منطقه زمانی خود را مدیریت کنید.</p>
      </header>

      <p
        v-if="successMessage"
        role="status"
        class="mb-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700"
      >
        {{ successMessage }}
      </p>

      <p
        v-if="serverError"
        role="alert"
        class="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
      >
        {{ serverError }}
      </p>

      <form class="space-y-5" novalidate @submit.prevent="handleSubmit">
        <div>
          <span class="mb-1 block text-sm font-medium text-gray-700">ایمیل</span>
          <p dir="ltr" class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-left text-gray-600">
            {{ authStore.user?.email }}
          </p>
        </div>

        <div>
          <label for="timezone" class="mb-1 block text-sm font-medium text-gray-700">
            منطقه زمانی
          </label>
          <select
            id="timezone"
            v-model="selectedTimezone"
            dir="ltr"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-left text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          >
            <option v-for="zone in availableTimezones" :key="zone" :value="zone">
              {{ zone }}
            </option>
          </select>
          <p class="mt-1 text-xs text-gray-500">
            این منطقه برای تعیین «امروز» و محاسبه زنجیره عادت‌ها استفاده می‌شود.
          </p>
        </div>

        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          ذخیره تغییرات
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
