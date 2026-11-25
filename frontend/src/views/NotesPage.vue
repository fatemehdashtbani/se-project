<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">روتین کده</p>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-10 pb-24 sm:px-6">
      <h1 class="text-2xl font-bold text-white">یادداشت‌ها</h1>
      <p class="mt-2 text-sm text-slate-400">ایده‌ها و نکته‌های روزانه‌ات را اینجا نگه دار.</p>

      <form
        class="mt-6 space-y-3 rounded-xl border border-slate-700 bg-slate-800/40 p-4"
        @submit.prevent="handleCreate"
      >
        <div>
          <label for="note-new-title" class="mb-1 block text-sm font-medium text-slate-200">
            عنوان
          </label>
          <input
            id="note-new-title"
            v-model="newTitle"
            type="text"
            class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          />
        </div>
        <div>
          <label for="note-new-content" class="mb-1 block text-sm font-medium text-slate-200">
            متن یادداشت
          </label>
          <textarea
            id="note-new-content"
            v-model="newContent"
            rows="3"
            class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          ></textarea>
        </div>
        <button
          type="submit"
          class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
        >
          ذخیره یادداشت
        </button>
      </form>

      <p
        v-if="errorMessage"
        role="alert"
        class="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
      >
        {{ errorMessage }}
      </p>

      <p v-if="noteStore.notes.length === 0" class="mt-6 text-sm text-slate-400">
        هنوز هیچ یادداشتی نساخته‌اید
      </p>

      <ul v-else class="mt-6 space-y-4">
        <li
          v-for="note in noteStore.notes"
          :key="note.id"
          class="rounded-xl border border-slate-700 bg-slate-800/40 p-4"
        >
          <form v-if="editingId === note.id" class="space-y-3" @submit.prevent="handleUpdate">
            <div>
              <label
                :for="`note-edit-title-${note.id}`"
                class="mb-1 block text-sm font-medium text-slate-200"
              >
                عنوان
              </label>
              <input
                :id="`note-edit-title-${note.id}`"
                v-model="editTitle"
                type="text"
                class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
              />
            </div>
            <div>
              <label
                :for="`note-edit-content-${note.id}`"
                class="mb-1 block text-sm font-medium text-slate-200"
              >
                متن یادداشت
              </label>
              <textarea
                :id="`note-edit-content-${note.id}`"
                v-model="editContent"
                rows="3"
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
            <h2 class="font-semibold text-white">{{ note.title }}</h2>
            <p
              v-if="note.content"
              class="mt-2 whitespace-pre-line text-sm text-slate-300"
            >
              {{ note.content }}
            </p>
            <div class="mt-4 flex gap-2">
              <button
                type="button"
                class="rounded-md border border-blue-500/50 px-3 py-1.5 text-xs font-medium text-blue-300 transition-colors hover:bg-blue-500/10 focus:outline-none focus:ring-2 focus:ring-blue-400/60"
                @click="startEdit(note)"
              >
                ویرایش
              </button>
              <button
                type="button"
                class="rounded-md border border-red-500/50 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-500/10 focus:outline-none focus:ring-2 focus:ring-red-400/60"
                @click="handleDelete(note.id)"
              >
                حذف
              </button>
            </div>
          </template>
        </li>
      </ul>
    </main>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import BottomNav from '@/components/BottomNav.vue';
import { useNoteStore, type Note } from '@/stores/notes';

const noteStore = useNoteStore();

const newTitle = ref('');
const newContent = ref('');
const editingId = ref<string | null>(null);
const editTitle = ref('');
const editContent = ref('');
const errorMessage = ref('');

async function loadNotes(): Promise<void> {
  try {
    await noteStore.fetchNotes();
  } catch {
    errorMessage.value = 'بارگذاری یادداشت‌ها ناموفق بود.';
  }
}

onMounted(() => {
  void loadNotes();
});

async function handleCreate(): Promise<void> {
  const title = newTitle.value.trim();

  if (!title) {
    errorMessage.value = 'عنوان یادداشت الزامی است.';
    return;
  }

  try {
    await noteStore.createNote(title, newContent.value.trim());
    newTitle.value = '';
    newContent.value = '';
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'ذخیره یادداشت ناموفق بود.';
  }
}

function startEdit(note: Note): void {
  editingId.value = note.id;
  editTitle.value = note.title;
  editContent.value = note.content;
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
    errorMessage.value = 'عنوان یادداشت الزامی است.';
    return;
  }

  try {
    await noteStore.updateNote(id, title, editContent.value.trim());
    editingId.value = null;
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'ویرایش یادداشت ناموفق بود.';
  }
}

async function handleDelete(id: string): Promise<void> {
  try {
    await noteStore.deleteNote(id);
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'حذف یادداشت ناموفق بود.';
  }
}
</script>
