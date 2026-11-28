<template>
  <aside
    dir="rtl"
    class="admin-sidebar flex h-screen w-64 shrink-0 flex-col overflow-y-auto p-3"
    aria-label="منوی پنل مدیریت"
  >
    <div class="flex items-center gap-3 px-2 py-4">
      <span
        class="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 text-white"
      >
        <el-icon :size="20"><DataLine /></el-icon>
      </span>
      <div class="min-w-0">
        <p class="text-lg font-extrabold text-white">روتین کده</p>
        <p class="text-xs text-violet-200">پنل مدیریت</p>
      </div>
    </div>

    <el-menu :default-active="activePath" router class="border-0">
      <el-menu-item v-for="item in managementItems" :key="item.to" :index="item.to">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </el-menu-item>
    </el-menu>

    <p class="px-3 pt-5 pb-1 text-xs font-bold text-violet-300">عمومی</p>

    <el-menu router class="border-0">
      <el-menu-item v-for="item in appItems" :key="item.to" :index="item.to">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </el-menu-item>
    </el-menu>

    <div class="mt-auto flex items-center gap-3 rounded-xl bg-white/10 p-3">
      <el-avatar :size="36" class="bg-white/20 text-white">
        {{ adminInitial }}
      </el-avatar>
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-bold text-white">{{ adminName }}</p>
        <p class="text-xs font-medium text-violet-200">{{ currentRoleLabel }}</p>
      </div>
      <button
        type="button"
        aria-label="خروج"
        class="rounded-lg p-2 text-violet-100 transition-colors hover:bg-white/15 hover:text-white focus:outline-none focus:ring-2 focus:ring-white/60"
        @click="handleLogout"
      >
        <el-icon :size="18"><SwitchButton /></el-icon>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  Collection,
  DataLine,
  House,
  Setting,
  SwitchButton,
  User,
  UserFilled,
} from '@element-plus/icons-vue';
import { roleLabels } from '@/shared/utils/paths';
import { useAuthStore } from '@/stores/auth';

const managementItems = [
  { to: '/admin', label: 'داشبورد', icon: DataLine },
  { to: '/admin/users', label: 'کاربران', icon: User },
  { to: '/admin/mentors', label: 'منتورها و منتورشیپ', icon: UserFilled },
  { to: '/admin/content', label: 'محتوا و روتین‌ها', icon: Collection },
  { to: '/admin/system', label: 'سیستم و لاگ‌ها', icon: Setting },
];

const appItems = [
  { to: '/dashboard', label: 'بازگشت به روتین‌ها', icon: House },
  { to: '/profile', label: 'پروفایل', icon: User },
];

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const activePath = computed(() => route.path);

const adminName = computed(() => {
  const user = authStore.user;
  if (!user) {
    return 'مدیر';
  }
  const parts = [user.first_name, user.last_name].filter(Boolean);
  return parts.length > 0 ? parts.join(' ') : (user.username ?? 'مدیر');
});

const adminInitial = computed(() => adminName.value.trim().charAt(0) || 'م');

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
