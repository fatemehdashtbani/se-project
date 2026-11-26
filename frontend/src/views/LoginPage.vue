<template>
  <AuthLayout title="ورود به حساب" subtitle="برای مدیریت روتین های خود وارد شوید">
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

      <fieldset>
        <legend class="mb-2 block text-sm text-slate-300">نقش</legend>
        <div
          class="grid grid-cols-2 gap-1 rounded-xl border border-slate-800 bg-slate-800/60 p-1"
          role="radiogroup"
          aria-label="نقش"
        >
          <button
            v-for="option in ROLE_OPTIONS"
            :key="option.value"
            type="button"
            role="radio"
            :aria-checked="role === option.value"
            :class="[
              'rounded-lg px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/50',
              role === option.value
                ? 'bg-slate-700 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200',
            ]"
            @click="selectRole(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </fieldset>

      <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
        <label class="flex items-center gap-2 whitespace-nowrap text-sm text-slate-300">
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
          class="whitespace-nowrap text-sm text-blue-400 transition-colors hover:text-blue-300"
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
import { useAuthStore, type UserRole } from '@/stores/auth';

type LoginMode = 'email' | 'mobile';
type LoginRole = 'user' | 'mentor';

const LOGIN_MODES: ReadonlyArray<{ value: LoginMode; label: string }> = [
  { value: 'email', label: 'ایمیل' },
  { value: 'mobile', label: 'موبایل' },
];

const ROLE_OPTIONS: ReadonlyArray<{ value: LoginRole; label: string }> = [
  { value: 'user', label: 'کاربر' },
  { value: 'mentor', label: 'مربی' },
];

const ROLE_MISMATCH_MESSAGE = 'نقش انتخاب شده با نقش واقعی حساب یکی نیست';

const authStore = useAuthStore();
const router = useRouter();

// Only the identifier is remembered, never the password: the password is not
// stored anywhere in the browser. An unchecked box removes the entry again.
const REMEMBERED_IDENTIFIER_KEY = 'routine-kade-remembered-identifier';

interface RememberedLogin {
  identifier: string;
  mode: LoginMode;
}

function readRememberedLogin(): RememberedLogin | null {
  try {
    const raw = localStorage.getItem(REMEMBERED_IDENTIFIER_KEY);
    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw) as Partial<RememberedLogin>;
    if (typeof parsed.identifier !== 'string' || !parsed.identifier) {
      return null;
    }

    return {
      identifier: parsed.identifier,
      mode: parsed.mode === 'mobile' ? 'mobile' : 'email',
    };
  } catch {
    return null;
  }
}

function storeRememberedLogin(value: RememberedLogin | null): void {
  try {
    if (value === null) {
      localStorage.removeItem(REMEMBERED_IDENTIFIER_KEY);
      return;
    }

    localStorage.setItem(REMEMBERED_IDENTIFIER_KEY, JSON.stringify(value));
  } catch {
    // Private mode or a full quota: forgetting the convenience is harmless.
  }
}

// A stored identifier only exists because the visitor asked to be remembered,
// so it is also the initial state of the checkbox.
const rememberedLogin = readRememberedLogin();

const mode = ref<LoginMode>(rememberedLogin?.mode ?? 'email');
const role = ref<LoginRole>('user');
const identifier = ref(rememberedLogin?.identifier ?? '');
const password = ref('');
const rememberMe = ref(rememberedLogin !== null);
const errors = reactive({ identifier: '', password: '' });
const serverError = ref('');

const identifierLabel = computed(() => (mode.value === 'email' ? 'ایمیل' : 'شماره تلفن'));

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

function selectRole(next: LoginRole): void {
  role.value = next;
  serverError.value = '';
}

/**
 * The selected role only chooses the destination; the account's server-owned
 * role stays authoritative. Choosing «مربی» for a non-mentor (or «کاربر» for a
 * mentor account) is refused instead of bouncing through the 403 page. Admins
 * still sign in through the «کاربر» option.
 */
function matchesAccountRole(selected: LoginRole, actual: UserRole): boolean {
  return selected === 'mentor' ? actual === 'mentor' : actual !== 'mentor';
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

  try {
    await authStore.login(identifierValue, password.value, rememberMe.value);

    const user = authStore.user;
    if (!user || !matchesAccountRole(role.value, user.role)) {
      try {
        // Do not leave a session behind that contradicts the chosen role.
        await authStore.logout();
      } catch {
        // The store clears its local identity even when revoke fails.
      }
      serverError.value = ROLE_MISMATCH_MESSAGE;
      return;
    }

    storeRememberedLogin(
      rememberMe.value ? { identifier: identifierValue, mode: mode.value } : null,
    );
    await router.push(role.value === 'mentor' ? '/mentor' : panelPath(user.role));
  } catch (error) {
    serverError.value = getPersianError(
      error instanceof ApiError ? error.code : 'UNKNOWN_ERROR',
    );
  }
}
</script>
