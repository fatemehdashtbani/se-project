<template>
  <aside
    dir="rtl"
    class="flex h-screen w-72 shrink-0 flex-col gap-1 overflow-y-auto border-l border-slate-800 bg-slate-900 p-4 text-slate-100"
    aria-label="منوی پنل مدیریت"
  >
    <div class="mb-4 flex items-center gap-2 px-2">
      <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-white">
        <HomeIcon class="h-5 w-5" />
      </span>
      <span class="text-lg font-extrabold">روتین کده</span>
    </div>

    <p class="px-3 pt-2 text-xs font-bold text-slate-500">پنل مدیریت</p>

    <RouterLink
      v-for="item in managementItems"
      :key="item.to"
      :to="item.to"
      class="rounded-xl px-3 py-2.5 text-sm text-slate-300 transition-colors hover:bg-slate-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
    >
      {{ item.label }}
    </RouterLink>

    <p class="px-3 pt-4 text-xs font-bold text-slate-500">عمومی</p>

    <RouterLink
      v-for="item in appItems"
      :key="item.to"
      :to="item.to"
      class="rounded-xl px-3 py-2.5 text-sm text-slate-300 transition-colors hover:bg-slate-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
    >
      {{ item.label }}
    </RouterLink>

    <div class="mt-auto flex items-center gap-3 rounded-xl bg-slate-800/60 p-3">
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-bold">{{ authStore.user?.first_name || 'مدیر' }}</p>
        <p class="text-xs font-medium text-blue-300">
          {{ currentRoleLabel }}
        </p>
      </div>
      <button
        type="button"
        aria-label="خروج"
        class="rounded-lg p-1.5 text-slate-300 transition-colors hover:bg-slate-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
        @click="handleLogout"
      >
        <LogoutIcon class="h-5 w-5" />
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import HomeIcon from '@/components/icons/HomeIcon.vue';
import LogoutIcon from '@/components/icons/LogoutIcon.vue';
import { roleLabels } from '@/shared/utils/paths';
import { useAuthStore } from '@/stores/auth';

const managementItems = [
  { to: '/admin', label: 'داشبورد' },
  { to: '/admin/users', label: 'کاربران' },
  { to: '/admin/plans', label: 'اشتراکها' },
];

const appItems = [
  { to: '/dashboard', label: 'بازگشت به روتینها' },
  { to: '/profile', label: 'پروفایل' },
];

const authStore = useAuthStore();
const router = useRouter();

const currentRoleLabel = computed(() =>
  authStore.user ? roleLabels[authStore.user.role] : 'میهمان',
);

async function handleLogout(): Promise<void> {
  try {
    await authStore.logout();
  } catch {
    // Local state is cleared by the store even when revoke fails.
  } finally {
    await router.push('/login');
  }
}
</script>
