<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100 lg:grid lg:grid-cols-2">
    <!-- First child, so RTL places the artwork on the right at desktop width. -->
    <div
      class="relative aspect-[4/3] w-full overflow-hidden lg:aspect-auto lg:h-auto lg:min-h-screen"
    >
      <img
        src="/login-bg.png"
        alt=""
        class="absolute inset-0 h-full w-full object-cover"
      />
      <div
        class="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/20 to-transparent"
      />
      <p class="absolute inset-x-0 bottom-0 p-6 text-sm font-medium text-white/90 lg:p-10">
        عادت‌های کوچک، تغییرات بزرگ
      </p>
    </div>

    <div
      class="flex min-h-[calc(100vh-75vw)] items-center justify-center px-4 py-10 lg:min-h-screen"
    >
      <div class="w-full max-w-md">
        <header class="mb-8 text-center">
          <p class="text-3xl font-extrabold tracking-tight text-white">روتین کده</p>
          <p class="mt-2 text-sm text-slate-400">همیار روزانه‌ی عادت‌ها و روتین‌ها</p>
        </header>

        <div v-if="title" class="mb-6 text-center">
          <h1 class="text-2xl font-bold text-white">{{ title }}</h1>
          <p v-if="subtitle" class="mt-2 text-sm text-slate-400">{{ subtitle }}</p>
        </div>

        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
}>();
</script>
