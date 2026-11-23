<template>
  <AuthLayout>
    <p
      v-if="serverError"
      role="alert"
      class="mb-5 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200"
    >
      {{ serverError }}
    </p>

    <form class="space-y-5" novalidate @submit.prevent="handleSubmit">
      <!-- The mobile tab is presented but not wired: the API only logs in by email. -->
      <div
        class="grid grid-cols-2 gap-1 rounded-xl border border-slate-800 bg-slate-800/60 p-1"
        role="tablist"
        aria-label="روش ورود"
      >
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'email'"
          class="rounded-lg bg-slate-700 px-3 py-2 text-sm font-medium text-white shadow-sm"
        >
          ایمیل
        </button>
        <button
          type="button"
          role="tab"
          disabled
          aria-disabled="true"
          title="به‌زودی"
          class="cursor-not-allowed rounded-lg px-3 py-2 text-sm font-medium text-slate-500"
        >
          موبایل
          <span class="ms-1 text-[10px] text-slate-500">به‌زودی</span>
        </button>
      </div>

      <div>
        <label for="email" class="mb-2 block text-sm text-slate-300">ایمیل</label>
        <input
          id="email"
          v-model="email"
          type="email"
          name="email"
          autocomplete="email"
          placeholder="you@example.com"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.email ? 'true' : 'false'"
          :aria-describedby="errors.email ? 'email-error' : undefined"
        />
        <p v-if="errors.email" id="email-error" role="alert" class="mt-2 text-sm text-rose-300">
          {{ errors.email }}
        </p>
      </div>

      <div>
        <label for="password" class="mb-2 block text-sm text-slate-300">رمز عبور</label>
        <input
          id="password"
          v-model="password"
          type="password"
          name="password"
          autocomplete="current-password"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.password ? 'true' : 'false'"
          :aria-describedby="errors.password ? 'password-error' : undefined"
        />
        <p
          v-if="errors.password"
          id="password-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.password }}
        </p>
      </div>

      <div class="flex items-center justify-between gap-3">
        <label class="flex items-center gap-2 text-sm text-slate-300">
          <input
            id="remember"
            v-model="rememberMe"
            type="checkbox"
            class="h-4 w-4 rounded border-slate-600 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-500/50"
          />
          مرا به خاطر بسپار
        </label>

        <a href="#" class="text-sm text-blue-400 transition-colors hover:text-blue-300">
          فراموشی رمز عبور؟
        </a>
      </div>

      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/60 disabled:cursor-not-allowed disabled:opacity-60"
      >
        ورود
      </button>
    </form>

    <p class="mt-8 text-center text-sm text-slate-400">
      <span>حساب کاربری ندارید؟</span>
      <RouterLink to="/register" class="ms-1 font-medium text-blue-400 hover:text-blue-300">
        ثبت‌نام
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
import { validateEmail, validatePassword } from '@/shared/utils/validation';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

const mode = ref<'email' | 'mobile'>('email');
const email = ref('');
const password = ref('');
const rememberMe = ref(false);
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
