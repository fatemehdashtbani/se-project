<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100 lg:grid lg:grid-cols-2">
    <!-- First child, so RTL places the artwork on the right at desktop width.
         On mobile it is a fixed backdrop, so scrolling the form never moves or
         crops the picture; the form rises over it as a bottom sheet. -->
    <div
      class="pointer-events-none fixed inset-0 overflow-hidden lg:relative lg:inset-auto lg:h-auto lg:min-h-screen"
    >
      <img
        src="/login-bg.png"
        alt=""
        class="absolute inset-0 h-full w-full object-cover"
      />
      <div
        class="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/20 to-transparent"
      />
      <p
        class="absolute inset-x-0 top-6 p-4 text-center text-sm font-medium text-white/90 [text-shadow:0_2px_10px_rgba(2,6,23,0.85)] lg:bottom-0 lg:top-auto lg:p-10 lg:text-right"
      >
        عادت‌های کوچک، تغییرات بزرگ
      </p>
    </div>

    <div
      class="relative z-10 flex min-h-screen items-end justify-center px-4 pb-6 pt-[22vh] lg:items-center lg:py-10"
    >
      <div
        class="w-full max-w-md rounded-3xl border border-slate-700/60 bg-slate-900/95 px-5 pb-8 pt-7 shadow-2xl backdrop-blur sm:px-7 lg:rounded-none lg:border-0 lg:bg-transparent lg:p-0 lg:shadow-none lg:backdrop-blur-none"
      >
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
