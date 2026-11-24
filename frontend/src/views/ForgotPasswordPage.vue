<template>
  <AuthLayout>
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

    <form class="space-y-5" novalidate @submit.prevent="handleSubmit">
      <div>
        <label for="forgot-email" class="mb-2 block text-sm text-slate-300">ایمیل</label>
        <input
          id="forgot-email"
          v-model="email"
          type="email"
          name="email"
          autocomplete="email"
          placeholder="you@example.com"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.email ? 'true' : 'false'"
          :aria-describedby="errors.email ? 'forgot-email-error' : undefined"
        />
        <p
          v-if="errors.email"
          id="forgot-email-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.email }}
        </p>
      </div>

      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/60 disabled:cursor-not-allowed disabled:opacity-60"
      >
        درخواست بازیابی رمز
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
import AuthLayout from '@/components/AuthLayout.vue';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { validateEmail } from '@/shared/utils/validation';
import { useAuthStore } from '@/stores/auth';

const SUCCESS_MESSAGE = 'درخواست بازیابی ثبت شد، ایمیل خود را بررسی کنید';

const authStore = useAuthStore();

const email = ref('');
const errors = reactive({ email: '' });
const successMessage = ref('');
const serverError = ref('');
const isSubmitting = ref(false);

async function handleSubmit(): Promise<void> {
  successMessage.value = '';
  serverError.value = '';
  errors.email = validateEmail(email.value) ?? '';

  if (errors.email !== '') {
    return;
  }

  isSubmitting.value = true;

  try {
    await authStore.forgotPassword(email.value.trim());
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
