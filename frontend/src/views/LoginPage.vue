<template>
  <AuthLayout title="ورود به حساب" subtitle="برای مدیریت روتینهای خود وارد شوید">
    <p
      v-if="serverError"
      role="alert"
      class="mb-5 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200"
    >
      {{ serverError }}
    </p>

    <form class="space-y-5" novalidate @submit.prevent="handleSubmit">
      <div
        class="grid grid-cols-2 gap-1 rounded-xl border border-slate-800 bg-slate-800/60 p-1"
        role="tablist"
        aria-label="روش ورود"
      >
        <button
          v-for="option in LOGIN_MODES"
          :key="option.value"
          type="button"
          role="tab"
          :aria-selected="mode === option.value"
          :class="[
            'rounded-lg px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/50',
            mode === option.value
              ? 'bg-slate-700 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200',
          ]"
          @click="selectMode(option.value)"
        >
          {{ option.label }}
        </button>
      </div>

      <div>
        <label for="identifier" class="mb-2 block text-sm text-slate-300">
          {{ identifierLabel }}
        </label>
        <input
          id="identifier"
          v-model="identifier"
          :type="mode === 'email' ? 'email' : 'tel'"
          name="identifier"
          :autocomplete="mode === 'email' ? 'email' : 'tel'"
          :placeholder="mode === 'email' ? 'you@example.com' : '09121234567'"
          dir="ltr"
          class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-left text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          :aria-invalid="errors.identifier ? 'true' : 'false'"
          :aria-describedby="errors.identifier ? 'identifier-error' : undefined"
        />
        <p
          v-if="errors.identifier"
          id="identifier-error"
          role="alert"
          class="mt-2 text-sm text-rose-300"
        >
          {{ errors.identifier }}
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

        <RouterLink
          to="/forgot-password"
          class="text-sm text-blue-400 transition-colors hover:text-blue-300"
        >
          فراموشی رمز عبور؟
        </RouterLink>
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
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import AuthLayout from '@/components/AuthLayout.vue';
import { ApiError } from '@/shared/api/client';
import { getPersianError } from '@/shared/utils/errors';
import { panelPath } from '@/shared/utils/paths';
import {
  normalizePhone,
  validateEmail,
  validatePassword,
  validatePhone,
} from '@/shared/utils/validation';
import { useAuthStore } from '@/stores/auth';

type LoginMode = 'email' | 'mobile';

const LOGIN_MODES: ReadonlyArray<{ value: LoginMode; label: string }> = [
  { value: 'email', label: 'ایمیل' },
  { value: 'mobile', label: 'موبایل' },
];

const authStore = useAuthStore();
const router = useRouter();

const mode = ref<LoginMode>('email');
const identifier = ref('');
const password = ref('');
const rememberMe = ref(false);
const errors = reactive({ identifier: '', password: '' });
const serverError = ref('');

const identifierLabel = computed(() => (mode.value === 'email' ? 'ایمیل' : 'شماره تلفن'));

const emit = defineEmits<{
  submit: [payload: { identifier: string; password: string }];
}>();

function selectMode(next: LoginMode): void {
  if (next === mode.value) {
    return;
  }

  mode.value = next;
  // The two modes hold different kinds of value, so carrying (or validating)
  // the old text under the new label would be misleading.
  identifier.value = '';
  errors.identifier = '';
}

function validate(): boolean {
  errors.identifier =
    (mode.value === 'email' ? validateEmail(identifier.value) : validatePhone(identifier.value)) ??
    '';
  errors.password = validatePassword(password.value) ?? '';

  return errors.identifier === '' && errors.password === '';
}

function normalizedIdentifier(): string {
  return mode.value === 'email' ? identifier.value.trim() : normalizePhone(identifier.value);
}

async function handleSubmit(): Promise<void> {
  if (!validate()) {
    return;
  }

  const identifierValue = normalizedIdentifier();
  serverError.value = '';
  emit('submit', { identifier: identifierValue, password: password.value });

  try {
    await authStore.login(identifierValue, password.value);
    await router.push(panelPath(authStore.user?.role));
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  }
}
</script>
