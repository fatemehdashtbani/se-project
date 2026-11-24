<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 px-4 py-12 text-slate-100">
    <div
      class="mx-auto w-full max-w-md rounded-2xl border border-slate-800 bg-slate-800/60 p-8 shadow-xl"
    >
      <header class="mb-6 flex items-start justify-between gap-3">
        <div>
          <h1 class="text-2xl font-bold text-white">پروفایل</h1>
          <p class="mt-2 text-sm text-slate-400">
            اطلاعات حساب و منطقه زمانی خود را مدیریت کنید.
          </p>
        </div>

        <RouterLink
          to="/dashboard"
          aria-label="بازگشت به داشبورد"
          class="rounded-full p-1.5 text-slate-300 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
        >
          <HomeIcon class="h-6 w-6" />
        </RouterLink>
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

      <form id="profile-form" class="space-y-4" novalidate @submit.prevent="handleProfileSubmit">
        <div>
          <label for="profile-first-name" class="mb-2 block text-sm font-medium text-slate-300">
            نام
          </label>
          <input
            id="profile-first-name"
            v-model="firstName"
            type="text"
            autocomplete="given-name"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          />
        </div>

        <div>
          <label for="profile-last-name" class="mb-2 block text-sm font-medium text-slate-300">
            نام خانوادگی
          </label>
          <input
            id="profile-last-name"
            v-model="lastName"
            type="text"
            autocomplete="family-name"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          />
        </div>

        <div>
          <label for="profile-phone" class="mb-2 block text-sm font-medium text-slate-300">
            شماره تلفن
          </label>
          <input
            id="profile-phone"
            v-model="phoneNumber"
            type="text"
            inputmode="tel"
            autocomplete="tel"
            dir="ltr"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          />
        </div>

        <div class="flex items-center justify-between gap-4 rounded-lg bg-slate-900/60 px-4 py-3">
          <span class="text-sm text-slate-400">ایمیل</span>
          <span class="text-sm font-medium text-white" dir="ltr">
            {{ authStore.user?.email }}
          </span>
        </div>

        <button
          type="submit"
          class="w-full rounded-xl bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
        >
          ذخیره تغییرات
        </button>
      </form>

      <form
        id="timezone-form"
        class="mt-6 space-y-4 border-t border-slate-700 pt-6"
        novalidate
        @submit.prevent="handleTimezoneSubmit"
      >
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
          class="w-full rounded-xl border border-blue-500/60 px-4 py-2.5 font-medium text-blue-200 transition-colors hover:bg-blue-500/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          ذخیره منطقه زمانی
        </button>
      </form>

      <div class="mt-6 space-y-4 border-t border-slate-700 pt-6">
        <button
          type="button"
          class="w-full rounded-xl border border-slate-700 px-4 py-2.5 font-medium text-slate-200 transition-colors hover:border-slate-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          :aria-expanded="showPasswordForm"
          aria-controls="password-form"
          @click="togglePasswordForm"
        >
          تغییر رمز عبور
        </button>

        <form
          v-if="showPasswordForm"
          id="password-form"
          class="space-y-4"
          novalidate
          @submit.prevent="handlePasswordSubmit"
        >
          <div>
            <label for="current-password" class="mb-2 block text-sm font-medium text-slate-300">
              رمز فعلی
            </label>
            <input
              id="current-password"
              v-model="currentPassword"
              type="password"
              autocomplete="current-password"
              dir="ltr"
              class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          <div>
            <label for="new-password" class="mb-2 block text-sm font-medium text-slate-300">
              رمز جدید
            </label>
            <input
              id="new-password"
              v-model="newPassword"
              type="password"
              autocomplete="new-password"
              dir="ltr"
              class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          <div>
            <label for="confirm-new-password" class="mb-2 block text-sm font-medium text-slate-300">
              تکرار رمز جدید
            </label>
            <input
              id="confirm-new-password"
              v-model="confirmNewPassword"
              type="password"
              autocomplete="new-password"
              dir="ltr"
              class="w-full rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          <button
            type="submit"
            class="w-full rounded-xl bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          >
            ثبت رمز جدید
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import HomeIcon from '@/components/icons/HomeIcon.vue';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { useAuthStore } from '@/stores/auth';

const PROFILE_SUCCESS_MESSAGE = 'اطلاعات با موفقیت ذخیره شد';
const TIMEZONE_SUCCESS_MESSAGE = 'منطقه زمانی با موفقیت ذخیره شد';
const PASSWORD_SUCCESS_MESSAGE = 'رمز عبور با موفقیت تغییر کرد';
const PASSWORD_MISMATCH_MESSAGE = 'تکرار رمز جدید مطابقت ندارد';
const PASSWORD_TOO_SHORT_MESSAGE = 'رمز جدید باید حداقل ۸ کاراکتر باشد';

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

const firstName = ref(authStore.user?.first_name ?? '');
const lastName = ref(authStore.user?.last_name ?? '');
const phoneNumber = ref(authStore.user?.phone_number ?? '');

const selectedTimezone = ref(authStore.user?.timezone ?? 'UTC');
const successMessage = ref('');
const serverError = ref('');
const isSubmitting = ref(false);

const showPasswordForm = ref(false);
const currentPassword = ref('');
const newPassword = ref('');
const confirmNewPassword = ref('');

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

function resetFeedback(): void {
  successMessage.value = '';
  serverError.value = '';
}

function handleProfileSubmit(): void {
  resetFeedback();
  // Mock save: the write endpoint for profile fields ships with a later feature.
  successMessage.value = PROFILE_SUCCESS_MESSAGE;
}

async function handleTimezoneSubmit(): Promise<void> {
  resetFeedback();
  isSubmitting.value = true;

  try {
    await authStore.updateTimezone(selectedTimezone.value);
    successMessage.value = TIMEZONE_SUCCESS_MESSAGE;
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  } finally {
    isSubmitting.value = false;
  }
}

function togglePasswordForm(): void {
  resetFeedback();
  showPasswordForm.value = !showPasswordForm.value;
  currentPassword.value = '';
  newPassword.value = '';
  confirmNewPassword.value = '';
}

function handlePasswordSubmit(): void {
  resetFeedback();

  if (newPassword.value.length < 8) {
    serverError.value = PASSWORD_TOO_SHORT_MESSAGE;
    return;
  }

  if (newPassword.value !== confirmNewPassword.value) {
    serverError.value = PASSWORD_MISMATCH_MESSAGE;
    return;
  }

  // Mock change: no backend endpoint exists yet, so only the UI reacts.
  showPasswordForm.value = false;
  currentPassword.value = '';
  newPassword.value = '';
  confirmNewPassword.value = '';
  successMessage.value = PASSWORD_SUCCESS_MESSAGE;
}
</script>
