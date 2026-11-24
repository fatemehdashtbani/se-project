<template>
  <AuthLayout
    title="تعیین رمز عبور جدید"
    subtitle="رمز تازه‌ای برای حساب خود انتخاب کنید"
  >
    <p
      v-if="successMessage"
      role="status"
      class="mb-5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200"
    >
      {{ successMessage }}
    </p>

    <p
      v-if="serverError"
      role="alert"
      class="mb-5 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200"
    >
      {{ serverError }}
    </p>

    <form v-if="token && !isDone" class="space-y-5" novalidate @submit.prevent="handleSubmit">
      <div>
        <label for="new-password" class="mb-2 block text-sm text-slate-300">
          رمز عبور جدید
        </label>
        <input
          id="new-password"
          v-model="password"
          type="password"
          name="new-password"
          autocomplete="new-password"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.password ? 'true' : 'false'"
          :aria-describedby="errors.password ? 'new-password-error' : undefined"
        />
        <p
          v-if="errors.password"
          id="new-password-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.password }}
        </p>
      </div>

      <div>
        <label for="confirm-password" class="mb-2 block text-sm text-slate-300">
          تکرار رمز عبور جدید
        </label>
        <input
          id="confirm-password"
          v-model="confirmation"
          type="password"
          name="confirm-password"
          autocomplete="new-password"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.confirmation ? 'true' : 'false'"
          :aria-describedby="errors.confirmation ? 'confirm-password-error' : undefined"
        />
        <p
          v-if="errors.confirmation"
          id="confirm-password-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.confirmation }}
        </p>
      </div>

      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/60 disabled:cursor-not-allowed disabled:opacity-60"
      >
        ذخیره رمز عبور جدید
      </button>
    </form>

    <p class="mt-8 text-center text-sm text-slate-400">
      <RouterLink to="/login" class="font-medium text-blue-400 hover:text-blue-300">
        بازگشت به صفحه ورود
      </RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute } from 'vue-router';
import AuthLayout from '@/components/AuthLayout.vue';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { MIN_PASSWORD_LENGTH, validatePassword } from '@/shared/utils/validation';
import { useAuthStore } from '@/stores/auth';

const SUCCESS_MESSAGE = 'رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید.';
const MISSING_TOKEN_MESSAGE = 'لینک بازیابی رمز نامعتبر است یا منقضی شده است';
const MISMATCH_MESSAGE = 'تکرار رمز عبور با رمز جدید یکسان نیست';

const authStore = useAuthStore();
const route = useRoute();

const rawToken = route.query.token;
const token = typeof rawToken === 'string' ? rawToken.trim() : '';

const password = ref('');
const confirmation = ref('');
const errors = reactive({ password: '', confirmation: '' });
const successMessage = ref('');
const serverError = ref(token === '' ? MISSING_TOKEN_MESSAGE : '');
const isSubmitting = ref(false);
const isDone = ref(false);

async function handleSubmit(): Promise<void> {
  successMessage.value = '';
  serverError.value = '';
  errors.password = validatePassword(password.value) ?? '';
  errors.confirmation =
    confirmation.value === password.value
      ? ''
      : confirmation.value === ''
        ? `رمز عبور باید حداقل ${MIN_PASSWORD_LENGTH} کاراکتر باشد`
        : MISMATCH_MESSAGE;

  if (errors.password !== '' || errors.confirmation !== '') {
    return;
  }

  isSubmitting.value = true;

  try {
    await authStore.resetPassword(token, password.value);
    successMessage.value = SUCCESS_MESSAGE;
    isDone.value = true;
    password.value = '';
    confirmation.value = '';
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  } finally {
    isSubmitting.value = false;
  }
}
</script>
