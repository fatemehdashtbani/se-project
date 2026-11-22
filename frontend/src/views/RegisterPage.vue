<template>
  <div dir="rtl" class="min-h-full flex items-center justify-center bg-gray-100 px-4 py-12">
    <div class="w-full max-w-md rounded-xl bg-white p-8 shadow-md">
      <header class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-gray-900">ثبت‌نام</h1>
        <p class="mt-2 text-sm text-gray-500">برای ساخت حساب، اطلاعات زیر را وارد کنید.</p>
      </header>

      <p
        v-if="serverError"
        role="alert"
        class="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
      >
        {{ serverError }}
      </p>

      <form class="space-y-5" novalidate @submit.prevent="handleSubmit">
        <div>
          <label for="register-email" class="mb-1 block text-sm font-medium text-gray-700">
            ایمیل
          </label>
          <input
            id="register-email"
            v-model="email"
            type="email"
            name="email"
            autocomplete="email"
            placeholder="you@example.com"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-right text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            :aria-invalid="errors.email ? 'true' : 'false'"
            :aria-describedby="errors.email ? 'register-email-error' : undefined"
          />
          <p
            v-if="errors.email"
            id="register-email-error"
            class="mt-1 text-xs text-red-600"
          >
            {{ errors.email }}
          </p>
        </div>

        <div>
          <label for="register-password" class="mb-1 block text-sm font-medium text-gray-700">
            رمز عبور
          </label>
          <input
            id="register-password"
            v-model="password"
            type="password"
            name="password"
            autocomplete="new-password"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-right text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            :aria-invalid="errors.password ? 'true' : 'false'"
            :aria-describedby="errors.password ? 'register-password-error' : undefined"
          />
          <p
            v-if="errors.password"
            id="register-password-error"
            class="mt-1 text-xs text-red-600"
          >
            {{ errors.password }}
          </p>
        </div>

        <div>
          <label
            for="register-confirm-password"
            class="mb-1 block text-sm font-medium text-gray-700"
          >
            تکرار رمز عبور
          </label>
          <input
            id="register-confirm-password"
            v-model="confirmPassword"
            type="password"
            name="confirm-password"
            autocomplete="new-password"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-right text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            :aria-invalid="errors.confirmPassword ? 'true' : 'false'"
            :aria-describedby="
              errors.confirmPassword ? 'register-confirm-password-error' : undefined
            "
          />
          <p
            v-if="errors.confirmPassword"
            id="register-confirm-password-error"
            class="mt-1 text-xs text-red-600"
          >
            {{ errors.confirmPassword }}
          </p>
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          ثبت‌نام
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        قبلاً ثبت‌نام کرده‌اید؟
        <RouterLink to="/login" class="font-medium text-blue-600 hover:text-blue-700">
          وارد شوید
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { validateEmail, validatePassword } from '@/shared/utils/validation';
import { useAuthStore } from '@/stores/auth';

const PASSWORD_MISMATCH_MESSAGE = 'رمز عبور و تکرار آن یکسان نیستند';

const authStore = useAuthStore();
const router = useRouter();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errors = reactive({ email: '', password: '', confirmPassword: '' });
const serverError = ref('');

function validate(): boolean {
  errors.email = validateEmail(email.value) ?? '';
  errors.password = validatePassword(password.value) ?? '';
  errors.confirmPassword =
    password.value !== confirmPassword.value ? PASSWORD_MISMATCH_MESSAGE : '';

  return errors.email === '' && errors.password === '' && errors.confirmPassword === '';
}

async function handleSubmit(): Promise<void> {
  serverError.value = '';

  if (!validate()) {
    return;
  }

  try {
    await authStore.register(email.value, password.value);
    await router.push('/dashboard');
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  }
}
</script>
