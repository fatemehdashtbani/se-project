<template>
  <div dir="rtl" class="flex min-h-screen bg-slate-950 text-slate-100">
    <AdminSidebar />

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="border-b border-slate-800 bg-slate-900/70 px-6 py-4">
        <h1 class="text-lg font-bold">پنل مدیریت</h1>
      </header>

      <main class="min-w-0 flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AdminSidebar from '@/components/AdminSidebar.vue';
</script>
