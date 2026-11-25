<template>
  <nav
    dir="rtl"
    class="fixed bottom-0 left-0 w-full z-50 border-t border-slate-700 bg-slate-900"
    aria-label="ناوبری اصلی"
  >
    <div class="flex items-center justify-around py-3">
      <RouterLink
        to="/dashboard"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <HomeIcon class="h-6 w-6" />
        <span class="text-[11px]">خانه</span>
      </RouterLink>

      <RouterLink
        to="/dashboard"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="h-6 w-6"
          aria-hidden="true"
        >
          <path d="M4 5h16v2H4V5Zm0 6h16v2H4v-2Zm0 6h16v2H4v-2Z" />
        </svg>
        <span class="text-[11px]">روتین‌ها</span>
      </RouterLink>

      <RouterLink
        to="/checklist"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="h-6 w-6"
          aria-hidden="true"
        >
          <path
            d="M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Zm2.7 8.3-1.4 1.4 3 3 6.4-6.4-1.4-1.4-5 5-1.6-1.6Z"
          />
        </svg>
        <span class="text-[11px]">چک‌لیست</span>
      </RouterLink>

      <RouterLink
        to="/calendar"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="h-6 w-6"
          aria-hidden="true"
        >
          <path
            d="M7 2h2v2h6V2h2v2h3a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3V2Zm13 8H5v10h15V10ZM5 8h15V6H5v2Z"
          />
        </svg>
        <span class="text-[11px]">تقویم</span>
      </RouterLink>

      <RouterLink
        to="/notes"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="h-6 w-6"
          aria-hidden="true"
        >
          <path
            d="M6 2h9l5 5v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Zm8 2v4h4l-4-4ZM8 12h8v2H8v-2Zm0 4h8v2H8v-2Z"
          />
        </svg>
        <span class="text-[11px]">یادداشت‌ها</span>
      </RouterLink>

      <RouterLink
        to="/profile"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <ProfileIcon class="h-6 w-6" />
        <span class="text-[11px]">پروفایل</span>
      </RouterLink>

      <button
        type="button"
        aria-label="خروج"
        class="flex flex-col items-center gap-1 rounded-lg px-1.5 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
        @click="handleLogout"
      >
        <LogoutIcon class="h-6 w-6" />
        <span class="text-[11px]">خروج</span>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import HomeIcon from '@/components/icons/HomeIcon.vue';
import LogoutIcon from '@/components/icons/LogoutIcon.vue';
import ProfileIcon from '@/components/icons/ProfileIcon.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

async function handleLogout(): Promise<void> {
  try {
    await authStore.logout();
  } catch {
    // The local session is already cleared by the store; a failed revoke
    // must not keep the visitor inside the protected area.
  } finally {
    await router.push('/login');
  }
}
</script>
