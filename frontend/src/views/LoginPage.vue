<template>
  <div dir="rtl" class="min-h-full flex items-center justify-center bg-gray-100 px-4 py-12">
    <div class="w-full max-w-md rounded-xl bg-white p-8 shadow-md">
      <header class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-gray-900">ورود به حساب کاربری</h1>
        <p class="mt-2 text-sm text-gray-500">برای ادامه، اطلاعات حساب خود را وارد کنید.</p>
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
          <label for="email" class="mb-1 block text-sm font-medium text-gray-700">ایمیل</label>
          <input
            id="email"
            v-model="email"
            type="email"
            name="email"
            autocomplete="email"
            placeholder="you@example.com"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-right text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            :aria-invalid="errors.email ? 'true' : 'false'"
            :aria-describedby="errors.email ? 'email-error' : undefined"
          />
          <p v-if="errors.email" id="email-error" role="alert" class="mt-1 text-sm text-red-600">
            {{ errors.email }}
          </p>
        </div>

        <div>
          <label for="password" class="mb-1 block text-sm font-medium text-gray-700">رمز عبور</label>
          <input
            id="password"
            v-model="password"
            type="password"
            name="password"
            autocomplete="current-password"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-right text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            :aria-invalid="errors.password ? 'true' : 'false'"
            :aria-describedby="errors.password ? 'password-error' : undefined"
          />
          <p
            v-if="errors.password"
            id="password-error"
            role="alert"
            class="mt-1 text-sm text-red-600"
          >
            {{ errors.password }}
          </p>
          <div class="mt-2 text-left">
            <a href="#" class="text-sm text-blue-600 hover:underline">فراموشی رمز عبور</a>
          </div>
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          ورود
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        <span>حساب کاربری ندارید؟</span>
        <RouterLink to="/register" class="mr-1 font-medium text-blue-600 hover:underline">
          ثبت‌نام
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

const authStore = useAuthStore();
const router = useRouter();

const email = ref('');
const password = ref('');
const errors = reactive({ email: '', password: '' });
const serverError = ref('');

const emit = defineEmits<{ submit: [payload: { email: string; password: string }] }>();

function validate(): boolean {
  errors.email = validateEmail(email.value) ?? '';
  errors.password = validatePassword(password.value) ?? '';

  return errors.email === '' && errors.password === '';
}

async function handleSubmit(): Promise<void> {
  if (!validate()) {
    return;
  }

  serverError.value = '';
  emit('submit', { email: email.value, password: password.value });

  try {
    await authStore.login(email.value, password.value);
    await router.push('/dashboard');
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  }
}
</script>
