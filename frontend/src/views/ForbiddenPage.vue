<template>
  <div dir="rtl" class="flex min-h-screen flex-col items-center justify-center gap-5 bg-slate-900 px-4 text-center text-slate-100">
    <p class="text-6xl font-extrabold text-blue-300">۴۰۳</p>
    <h1 class="text-2xl font-bold">دسترسی غیرمجاز</h1>
    <p class="max-w-md leading-8 text-slate-400">
      این بخش مخصوص حساب {{ requiredLabel }} است و حساب فعالی که با آن وارد شدهاید
      ({{ currentLabel }}) دسترسی لازم را ندارد.
    </p>
    <RouterLink
      :to="panelPath(authStore.user?.role)"
      class="rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
    >
      بازگشت به پنل کاربری
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { panelPath, roleLabels } from '@/shared/utils/paths';
import { useAuthStore, type UserRole } from '@/stores/auth';

const route = useRoute();
const authStore = useAuthStore();

const requiredLabel = computed(() => {
  const required = route.query.required as UserRole | undefined;
  return required && required in roleLabels ? roleLabels[required] : roleLabels.admin;
});

const currentLabel = computed(() =>
  authStore.user ? roleLabels[authStore.user.role] : 'میهمان',
);
</script>
