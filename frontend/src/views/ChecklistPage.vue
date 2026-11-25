<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">روتین کده</p>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-10 pb-24 sm:px-6">
      <h1 class="text-2xl font-bold text-white">چک‌لیست</h1>
      <p class="mt-2 text-sm text-slate-400">کارهای روزانه را بنویس و با یک کلیک تیک بزن.</p>

      <form class="mt-6 flex flex-col gap-3 sm:flex-row" @submit.prevent="handleCreate">
        <input
          id="checklist-new-title"
          v-model="newTitle"
          type="text"
          aria-label="عنوان کار جدید"
          placeholder="مثلاً نوشیدن آب"
          class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
        />
        <button
          type="submit"
          class="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
        >
          افزودن
        </button>
      </form>

      <p
        v-if="errorMessage"
        role="alert"
        class="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
      >
        {{ errorMessage }}
      </p>

      <p v-if="total > 0" class="mt-6 text-sm text-slate-400">{{ progressLabel }}</p>

      <p v-if="total === 0" class="mt-6 text-sm text-slate-400">
        هنوز هیچ کاری به چک‌لیست اضافه نکرده‌اید
      </p>

      <ul v-else class="mt-4 space-y-3">
        <li
          v-for="item in checklistStore.items"
          :key="item.id"
          class="flex items-center gap-3 rounded-xl border border-slate-700 bg-slate-800/40 px-4 py-3"
        >
          <input
            :id="`checklist-item-${item.id}`"
            type="checkbox"
            :checked="item.is_done"
            class="h-5 w-5 cursor-pointer rounded border-slate-500 bg-slate-800 accent-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500/60"
            @change="toggle(item)"
          />
          <label
            :for="`checklist-item-${item.id}`"
            class="flex-1 cursor-pointer text-sm"
            :class="item.is_done ? 'text-slate-500 line-through' : 'text-slate-100'"
          >
            {{ item.title }}
          </label>
          <button
            type="button"
            class="rounded-md border border-red-500/50 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-500/10 focus:outline-none focus:ring-2 focus:ring-red-400/60"
            @click="handleDelete(item.id)"
          >
            حذف
          </button>
        </li>
      </ul>
    </main>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import BottomNav from '@/components/BottomNav.vue';
import { useChecklistStore, type ChecklistItem } from '@/stores/checklist';
import { toPersianDigits } from '@/shared/utils/calendar';

const checklistStore = useChecklistStore();

const newTitle = ref('');
const errorMessage = ref('');

const total = computed(() => checklistStore.items.length);
const done = computed(() => checklistStore.items.filter((item) => item.is_done).length);
const progressLabel = computed(
  () => `${toPersianDigits(done.value)} از ${toPersianDigits(total.value)} انجام شده`,
);

async function loadItems(): Promise<void> {
  try {
    await checklistStore.fetchItems();
  } catch {
    errorMessage.value = 'بارگذاری چک‌لیست ناموفق بود.';
  }
}

onMounted(() => {
  void loadItems();
});

async function handleCreate(): Promise<void> {
  const title = newTitle.value.trim();

  if (!title) {
    errorMessage.value = 'عنوان کار الزامی است.';
    return;
  }

  try {
    await checklistStore.createItem(title);
    newTitle.value = '';
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'افزودن به چک‌لیست ناموفق بود.';
  }
}

async function toggle(item: ChecklistItem): Promise<void> {
  try {
    await checklistStore.setDone(item.id, !item.is_done);
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'به‌روزرسانی چک‌لیست ناموفق بود.';
  }
}

async function handleDelete(id: string): Promise<void> {
  try {
    await checklistStore.deleteItem(id);
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'حذف مورد ناموفق بود.';
  }
}
</script>
