<template>
  <nav
    dir="rtl"
    class="fixed bottom-0 left-0 w-full z-50 border-t border-slate-700 bg-slate-900"
    aria-label="ناوبری اصلی"
  >
    <div class="flex items-center justify-around py-3">
      <RouterLink
        to="/dashboard"
        class="flex flex-col items-center gap-1 rounded-lg px-3 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <HomeIcon class="h-6 w-6" />
        <span class="text-xs">خانه</span>
      </RouterLink>

      <RouterLink
        to="/dashboard"
        class="flex flex-col items-center gap-1 rounded-lg px-3 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
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
        <span class="text-xs">روتینها</span>
      </RouterLink>

      <RouterLink
        to="/profile"
        class="flex flex-col items-center gap-1 rounded-lg px-3 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
      >
        <ProfileIcon class="h-6 w-6" />
        <span class="text-xs">پروفایل</span>
      </RouterLink>

      <button
        type="button"
        aria-label="خروج"
        class="flex flex-col items-center gap-1 rounded-lg px-3 py-1 text-slate-400 transition-colors hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
        @click="handleLogout"
      >
        <LogoutIcon class="h-6 w-6" />
        <span class="text-xs">خروج</span>
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
