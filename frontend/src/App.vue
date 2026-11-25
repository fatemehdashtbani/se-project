<template>
  <ThemeToggle />
  <TodayReminders />
  <RouterView />
</template>

<script setup lang="ts">
import ThemeToggle from '@/components/ThemeToggle.vue';
import TodayReminders from '@/components/TodayReminders.vue';
</script>
