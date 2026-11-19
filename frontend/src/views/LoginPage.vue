<template>
  <div dir="rtl" class="min-h-full flex items-center justify-center bg-gray-100 px-4 py-12">
    <div class="w-full max-w-md rounded-xl bg-white p-8 shadow-md">
      <header class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-gray-900">ورود به حساب کاربری</h1>
        <p class="mt-2 text-sm text-gray-500">برای ادامه، اطلاعات حساب خود را وارد کنید.</p>
      </header>

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
          class="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
        >
          ورود
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        <span>حساب کاربری ندارید؟</span>
        <a href="#" class="mr-1 font-medium text-blue-600 hover:underline">ثبت‌نام</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';

const MIN_PASSWORD_LENGTH = 8;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const email = ref('');
const password = ref('');
const errors = reactive({ email: '', password: '' });

const emit = defineEmits<{ submit: [payload: { email: string; password: string }] }>();

function validate(): boolean {
  const trimmedEmail = email.value.trim();

  if (trimmedEmail === '') {
    errors.email = 'ایمیل الزامی است';
  } else if (!EMAIL_PATTERN.test(trimmedEmail)) {
    errors.email = 'فرمت ایمیل معتبر نیست';
  } else {
    errors.email = '';
  }

  errors.password =
    password.value.length < MIN_PASSWORD_LENGTH ? 'رمز عبور باید حداقل ۸ کاراکتر باشد' : '';

  return errors.email === '' && errors.password === '';
}

function handleSubmit(): void {
  if (!validate()) {
    return;
  }

  emit('submit', { email: email.value, password: password.value });
}
</script>
