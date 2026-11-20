<template>
  <div dir="rtl" class="min-h-full flex flex-col items-center justify-center gap-4 bg-gray-100 px-4 py-12">
    <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
    <button
      type="button"
      class="rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
      @click="handleLogout"
    >
      خروج
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

async function handleLogout(): Promise<void> {
  await authStore.logout();
  await router.push('/login');
}
</script>
