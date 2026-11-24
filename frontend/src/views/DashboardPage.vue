<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">روتین کده</p>

        <div class="flex items-center gap-3 sm:gap-5">
          <RouterLink
            to="/profile"
            aria-label="پروفایل"
            class="rounded-full p-1 text-slate-300 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          >
            <ProfileIcon class="h-7 w-7" />
          </RouterLink>

          <button
            type="button"
            class="rounded-lg px-2 py-1.5 text-sm font-medium text-white transition-colors hover:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500/60"
            @click="handleLogout"
          >
            خروج از حساب
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <h1 class="text-2xl font-bold text-white">داشبورد</h1>
      <p class="mt-2 text-sm text-slate-400">
        به روتین کده خوش آمدید؛ روتین‌های شما به‌زودی اینجا نمایش داده می‌شوند.
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import ProfileIcon from '@/components/icons/ProfileIcon.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

async function handleLogout(): Promise<void> {
  try {
    await authStore.logout();
  } catch {
    // The store has already dropped the local user in its own `finally`;
    // a failed revoke must not trap the visitor inside the protected area.
  } finally {
    await router.push('/login');
  }
}
</script>
