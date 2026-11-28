<template>
  <div dir="rtl" class="admin-shell flex min-h-screen">
    <AdminSidebar />

    <div class="flex min-w-0 flex-1 flex-col">
      <header
        class="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b border-violet-100 bg-white/90 px-4 py-3 backdrop-blur sm:px-6"
      >
        <div class="min-w-0">
          <p class="text-xs font-medium text-violet-500">پنل مدیریت روتین کده</p>
          <h1 class="truncate text-lg font-extrabold text-violet-900">
            {{ pageTitle }}
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <el-tag effect="light" round>{{ adminName }}</el-tag>
          <el-button text @click="goToApp">بازگشت به اپ</el-button>
        </div>
      </header>

      <main class="min-w-0 flex-1 p-4 sm:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AdminSidebar from '@/components/AdminSidebar.vue';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const pageTitle = computed(() => (route.meta.title as string | undefined) ?? 'داشبورد');

const adminName = computed(() => {
  const user = authStore.user;
  if (!user) {
    return 'مدیر سامانه';
  }
  const parts = [user.first_name, user.last_name].filter(Boolean);
  return parts.length > 0 ? parts.join(' ') : (user.username ?? 'مدیر سامانه');
});

function goToApp(): void {
  void router.push('/dashboard');
}
</script>
