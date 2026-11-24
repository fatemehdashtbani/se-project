<template>
  <section class="rounded-2xl border border-slate-800 bg-slate-900/60 px-6 py-14 text-center">
    <h2 class="text-xl font-bold text-white">{{ title }}</h2>
    <p class="mx-auto mt-3 max-w-md leading-8 text-slate-400">
      این بخش در حال توسعه است. عملیات مدیریتی مربوط به آن پس از تکمیل سرویسهای سمت سرور
      افزوده میشود.
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const title = computed(() => (route.meta.title as string | undefined) ?? 'بخش مدیریتی');
</script>
