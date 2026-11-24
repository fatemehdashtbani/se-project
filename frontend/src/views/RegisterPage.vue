<template>
  <AuthLayout
    title="ایجاد حساب کاربری جدید"
    subtitle="با چند گام ساده روتین خود را آغاز کنید"
  >
    <p
      v-if="serverError"
      role="alert"
      class="mb-5 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200"
    >
      {{ serverError }}
    </p>

    <form class="space-y-4" novalidate @submit.prevent="handleSubmit">
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label for="register-first-name" class="mb-2 block text-sm text-slate-300">
            نام
          </label>
          <input
            id="register-first-name"
            v-model="firstName"
            type="text"
            name="firstName"
            autocomplete="given-name"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-right text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            :aria-invalid="errors.firstName ? 'true' : 'false'"
            :aria-describedby="errors.firstName ? 'register-first-name-error' : undefined"
          />
          <p
            v-if="errors.firstName"
            id="register-first-name-error"
            role="alert"
            class="mt-2 text-sm text-rose-300"
          >
            {{ errors.firstName }}
          </p>
        </div>

        <div>
          <label for="register-last-name" class="mb-2 block text-sm text-slate-300">
            نام خانوادگی
          </label>
          <input
            id="register-last-name"
            v-model="lastName"
            type="text"
            name="lastName"
            autocomplete="family-name"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-right text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            :aria-invalid="errors.lastName ? 'true' : 'false'"
            :aria-describedby="errors.lastName ? 'register-last-name-error' : undefined"
          />
          <p
            v-if="errors.lastName"
            id="register-last-name-error"
            role="alert"
            class="mt-2 text-sm text-rose-300"
          >
            {{ errors.lastName }}
          </p>
        </div>
      </div>

      <div>
        <label for="register-username" class="mb-2 block text-sm text-slate-300">
          نام کاربری
        </label>
        <input
          id="register-username"
          v-model="username"
          type="text"
          name="username"
          autocomplete="username"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.username ? 'true' : 'false'"
          :aria-describedby="errors.username ? 'register-username-error' : undefined"
        />
        <p
          v-if="errors.username"
          id="register-username-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.username }}
        </p>
      </div>

      <div>
        <label for="register-phone" class="mb-2 block text-sm text-slate-300">
          شماره تلفن
        </label>
        <input
          id="register-phone"
          v-model="phoneNumber"
          type="tel"
          name="phoneNumber"
          autocomplete="tel"
          dir="ltr"
          placeholder="09121234567"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.phoneNumber ? 'true' : 'false'"
          :aria-describedby="errors.phoneNumber ? 'register-phone-error' : undefined"
        />
        <p
          v-if="errors.phoneNumber"
          id="register-phone-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.phoneNumber }}
        </p>
      </div>

      <div>
        <label for="register-email" class="mb-2 block text-sm text-slate-300">ایمیل</label>
        <input
          id="register-email"
          v-model="email"
          type="email"
          name="email"
          autocomplete="email"
          dir="ltr"
          placeholder="you@example.com"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.email ? 'true' : 'false'"
          :aria-describedby="errors.email ? 'register-email-error' : undefined"
        />
        <p
          v-if="errors.email"
          id="register-email-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.email }}
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label for="register-password" class="mb-2 block text-sm text-slate-300">
            رمز عبور
          </label>
          <input
            id="register-password"
            v-model="password"
            type="password"
            name="password"
            autocomplete="new-password"
            dir="ltr"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            :aria-invalid="errors.password ? 'true' : 'false'"
            :aria-describedby="errors.password ? 'register-password-error' : undefined"
          />
          <p
            v-if="errors.password"
            id="register-password-error"
            role="alert"
            class="mt-2 text-sm text-rose-300"
          >
            {{ errors.password }}
          </p>
        </div>

        <div>
          <label for="register-confirm-password" class="mb-2 block text-sm text-slate-300">
            تکرار رمز عبور
          </label>
          <input
            id="register-confirm-password"
            v-model="confirmPassword"
            type="password"
            name="confirmPassword"
            autocomplete="new-password"
            dir="ltr"
            class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            :aria-invalid="errors.confirmation ? 'true' : 'false'"
            :aria-describedby="
              errors.confirmation ? 'register-confirm-password-error' : undefined
            "
          />
          <p
            v-if="errors.confirmation"
            id="register-confirm-password-error"
            role="alert"
            class="mt-2 text-sm text-rose-300"
          >
            {{ errors.confirmation }}
          </p>
        </div>
      </div>

      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/60 disabled:cursor-not-allowed disabled:opacity-60"
      >
        ثبت‌نام
      </button>
    </form>

    <p class="mt-8 text-center text-sm text-slate-400">
      قبلاً ثبت‌نام کرده‌اید؟
      <RouterLink to="/login" class="ms-1 font-medium text-blue-400 hover:text-blue-300">
        وارد شوید
      </RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import AuthLayout from '@/components/AuthLayout.vue';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { panelPath } from '@/shared/utils/paths';
import {
  FIRST_NAME_REQUIRED_MESSAGE,
  LAST_NAME_REQUIRED_MESSAGE,
  normalizePhone,
  validateEmail,
  validatePassword,
  validatePhone,
  validateRequired,
  validateUsername,
} from '@/shared/utils/validation';
import { useAuthStore } from '@/stores/auth';

const PASSWORD_MISMATCH_MESSAGE = 'رمز عبور و تکرار آن یکسان نیستند';

const authStore = useAuthStore();
const router = useRouter();

const firstName = ref('');
const lastName = ref('');
const username = ref('');
const phoneNumber = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errors = reactive({
  firstName: '',
  lastName: '',
  username: '',
  phoneNumber: '',
  email: '',
  password: '',
  confirmation: '',
});
const serverError = ref('');

function validate(): boolean {
  errors.firstName = validateRequired(firstName.value, FIRST_NAME_REQUIRED_MESSAGE) ?? '';
  errors.lastName = validateRequired(lastName.value, LAST_NAME_REQUIRED_MESSAGE) ?? '';
  errors.username = validateUsername(username.value) ?? '';
  errors.phoneNumber = validatePhone(phoneNumber.value) ?? '';
  errors.email = validateEmail(email.value) ?? '';
  errors.password = validatePassword(password.value) ?? '';
  errors.confirmation =
    password.value !== confirmPassword.value ? PASSWORD_MISMATCH_MESSAGE : '';

  return Object.values(errors).every((message) => message === '');
}

async function handleSubmit(): Promise<void> {
  serverError.value = '';

  if (!validate()) {
    return;
  }

  try {
    await authStore.register({
      email: email.value.trim(),
      password: password.value,
      username: username.value.trim(),
      firstName: firstName.value.trim(),
      lastName: lastName.value.trim(),
      phoneNumber: normalizePhone(phoneNumber.value),
    });
    await router.push(panelPath(authStore.user?.role));
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  }
}
</script>
