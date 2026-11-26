<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-5xl items-center px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">روتین کده</p>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-10 pb-24 sm:px-6">
      <h1 class="text-2xl font-bold text-white">داشبورد</h1>
      <p class="mt-2 text-sm text-slate-400">
        کاربر {{ authStore.user?.first_name || authStore.user?.username || 'کاربر' }} به روتین کده
        خوش آمدید.
      </p>

      <section class="mt-10 rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <h2 class="text-xl font-semibold text-white">روتین‌های من</h2>
          <button
            v-if="!showCreateForm"
            type="button"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
            @click="openCreateForm"
          >
            + روتین جدید
          </button>
        </div>

        <p
          v-if="errorMessage"
          role="alert"
          class="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
        >
          {{ errorMessage }}
        </p>

        <p v-if="routineStore.routines.length === 0" class="mt-5 text-sm text-slate-400">
          هنوز هیچ روتینی نساخته‌اید
        </p>

        <ul v-else class="mt-5 grid gap-4 sm:grid-cols-2">
          <li
            v-for="routine in routineStore.routines"
            :key="routine.id"
            class="rounded-xl border border-slate-700 bg-slate-900/70 p-4"
          >
            <form
              v-if="editingId === routine.id"
              class="space-y-3"
              @submit.prevent="handleUpdate"
            >
              <div>
                <label
                  :for="`routine-edit-title-${routine.id}`"
                  class="mb-1 block text-sm font-medium text-slate-200"
                >
                  عنوان
                </label>
                <input
                  :id="`routine-edit-title-${routine.id}`"
                  v-model="editTitle"
                  type="text"
                  class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
                />
              </div>
              <div>
                <label
                  :for="`routine-edit-description-${routine.id}`"
                  class="mb-1 block text-sm font-medium text-slate-200"
                >
                  توضیحات
                </label>
                <textarea
                  :id="`routine-edit-description-${routine.id}`"
                  v-model="editDescription"
                  rows="2"
                  class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
                ></textarea>
              </div>
              <div class="flex gap-2">
                <button
                  type="submit"
                  class="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
                >
                  ذخیره
                </button>
                <button
                  type="button"
                  class="rounded-md border border-slate-600 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:bg-slate-700/50 focus:outline-none focus:ring-2 focus:ring-slate-400/60"
                  @click="cancelEdit"
                >
                  انصراف
                </button>
              </div>
            </form>

            <template v-else>
              <h3 class="font-semibold text-white">{{ routine.title }}</h3>
              <p v-if="routine.description" class="mt-1 text-sm text-slate-400">
                {{ routine.description }}
              </p>
              <div class="mt-4 flex gap-2">
                <button
                  type="button"
                  class="rounded-md border border-blue-500/50 px-3 py-1.5 text-xs font-medium text-blue-300 transition-colors hover:bg-blue-500/10 focus:outline-none focus:ring-2 focus:ring-blue-400/60"
                  @click="startEdit(routine)"
                >
                  ویرایش
                </button>
                <button
                  type="button"
                  class="rounded-md border border-red-500/50 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-500/10 focus:outline-none focus:ring-2 focus:ring-red-400/60"
                  @click="handleDelete(routine.id)"
                >
                  حذف
                </button>
              </div>
            </template>
          </li>
        </ul>

        <form
          v-if="showCreateForm"
          class="mt-5 space-y-4 rounded-xl border border-slate-700 bg-slate-900/70 p-4"
          @submit.prevent="handleCreate"
        >
          <div>
            <label for="routine-title" class="mb-1 block text-sm font-medium text-slate-200">
              عنوان
            </label>
            <input
              id="routine-title"
              v-model="newTitle"
              type="text"
              class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
            />
          </div>
          <div>
            <label for="routine-description" class="mb-1 block text-sm font-medium text-slate-200">
              توضیحات
            </label>
            <textarea
              id="routine-description"
              v-model="newDescription"
              rows="2"
              class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
            ></textarea>
          </div>
          <button
            type="submit"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
          >
            ذخیره
          </button>
        </form>
      </section>

      <section class="mt-10">
        <h2 class="text-xl font-semibold text-white">ابزارهای من</h2>
        <div class="mt-4 grid gap-4 sm:grid-cols-3">
          <RouterLink
            to="/checklist"
            class="rounded-2xl border border-slate-800 bg-slate-800/40 p-5 transition-colors hover:border-blue-500/60 hover:bg-slate-800/70 focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          >
            <h3 class="font-semibold text-white">چک‌لیست</h3>
            <p class="mt-1 text-sm text-slate-400">کارهای روزانه را تیک بزن.</p>
          </RouterLink>
          <RouterLink
            to="/calendar"
            class="rounded-2xl border border-slate-800 bg-slate-800/40 p-5 transition-colors hover:border-blue-500/60 hover:bg-slate-800/70 focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          >
            <h3 class="font-semibold text-white">تقویم</h3>
            <p class="mt-1 text-sm text-slate-400">رویدادهای ماه را ببین.</p>
          </RouterLink>
          <RouterLink
            to="/notes"
            class="rounded-2xl border border-slate-800 bg-slate-800/40 p-5 transition-colors hover:border-blue-500/60 hover:bg-slate-800/70 focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          >
            <h3 class="font-semibold text-white">یادداشت‌ها</h3>
            <p class="mt-1 text-sm text-slate-400">ایده‌ها را ثبت کن.</p>
          </RouterLink>
        </div>
      </section>

      <MentorApplicationSection v-if="authStore.user?.role === 'user'" />

      <MentorSection v-if="authStore.user?.role === 'user'" />

      <section
        v-else-if="authStore.user?.role === 'mentor'"
        class="mt-10 rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6"
      >
        <h2 class="text-xl font-semibold text-white">مربی/مشاور</h2>
        <p class="mt-2 text-sm text-slate-400">به میز کار مربی بروید.</p>
        <RouterLink
          to="/mentor"
          class="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
        >
          میز کار مربی
        </RouterLink>
      </section>
    </main>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import BottomNav from '@/components/BottomNav.vue';
import MentorApplicationSection from '@/components/MentorApplicationSection.vue';
import MentorSection from '@/components/MentorSection.vue';
import { useAuthStore } from '@/stores/auth';
import { useRoutineStore, type Routine } from '@/stores/routine';

const authStore = useAuthStore();
const routineStore = useRoutineStore();

const showCreateForm = ref(false);
const newTitle = ref('');
const newDescription = ref('');
const editingId = ref<string | null>(null);
const editTitle = ref('');
const editDescription = ref('');
const errorMessage = ref('');

async function loadRoutines(): Promise<void> {
  try {
    await routineStore.fetchRoutines();
  } catch {
    errorMessage.value = 'بارگذاری روتین‌ها ناموفق بود.';
  }
}

onMounted(() => {
  void loadRoutines();
});

function openCreateForm(): void {
  showCreateForm.value = true;
  editingId.value = null;
  newTitle.value = '';
  newDescription.value = '';
  errorMessage.value = '';
}

async function handleCreate(): Promise<void> {
  const title = newTitle.value.trim();

  if (!title) {
    errorMessage.value = 'عنوان روتین الزامی است.';
    return;
  }

  try {
    await routineStore.createRoutine(title, newDescription.value.trim() || null);
    showCreateForm.value = false;
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'ذخیره روتین ناموفق بود.';
  }
}

function startEdit(routine: Routine): void {
  showCreateForm.value = false;
  editingId.value = routine.id;
  editTitle.value = routine.title;
  editDescription.value = routine.description ?? '';
  errorMessage.value = '';
}

function cancelEdit(): void {
  editingId.value = null;
}

async function handleUpdate(): Promise<void> {
  const id = editingId.value;
  const title = editTitle.value.trim();

  if (!id) {
    return;
  }

  if (!title) {
    errorMessage.value = 'عنوان روتین الزامی است.';
    return;
  }

  try {
    await routineStore.updateRoutine(id, title, editDescription.value.trim() || null);
    editingId.value = null;
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'ویرایش روتین ناموفق بود.';
  }
}

async function handleDelete(id: string): Promise<void> {
  try {
    await routineStore.deleteRoutine(id);
  } catch {
    errorMessage.value = 'حذف روتین ناموفق بود.';
  }
}
</script>
