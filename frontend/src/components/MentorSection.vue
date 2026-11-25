<template>
  <section class="mt-10 rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6">
    <h2 class="text-xl font-semibold text-white">مربی/مشاور</h2>

    <p
      v-if="errorMessage"
      role="alert"
      class="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
    >
      {{ errorMessage }}
    </p>

    <div v-if="mentorStore.isLoading && !mentorStore.selectedMentor && mentorStore.mentors.length === 0" class="mt-5 text-sm text-slate-400">
      در حال بارگذاری...
    </div>

    <!-- No mentor selected: directory -->
    <div v-else-if="!mentorStore.selectedMentor">
      <p v-if="mentorStore.mentors.length === 0" class="mt-5 text-sm text-slate-400">
        هنوز مربی‌ای ثبت نشده است.
      </p>
      <ul v-else class="mt-5 grid gap-4 sm:grid-cols-2">
        <li
          v-for="mentor in mentorStore.mentors"
          :key="mentor.id"
          class="rounded-xl border border-slate-700 bg-slate-900/70 p-4"
        >
          <h3 class="font-semibold text-white">{{ mentor.name }}</h3>
          <p v-if="mentor.headline" class="mt-1 text-sm text-blue-300">{{ mentor.headline }}</p>
          <p v-if="mentor.bio" class="mt-2 text-sm text-slate-400">{{ mentor.bio }}</p>
          <button
            type="button"
            class="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
            @click="handleSelect(mentor.id)"
          >
            انتخاب مربی
          </button>
        </li>
      </ul>
    </div>

    <!-- Selected mentor -->
    <div v-else class="mt-5 space-y-6">
      <div class="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 class="font-semibold text-white">{{ mentorStore.selectedMentor.name }}</h3>
            <p v-if="mentorStore.selectedMentor.headline" class="mt-1 text-sm text-blue-300">
              {{ mentorStore.selectedMentor.headline }}
            </p>
            <p v-if="mentorStore.selectedMentor.bio" class="mt-2 text-sm text-slate-400">
              {{ mentorStore.selectedMentor.bio }}
            </p>
          </div>
          <button
            type="button"
            class="rounded-md border border-slate-600 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:bg-slate-700/50 focus:outline-none focus:ring-2 focus:ring-slate-400/60"
            @click="handleChangeMentor"
          >
            تغییر مربی
          </button>
        </div>
      </div>

      <!-- Thread -->
      <div class="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <h3 class="mb-3 font-semibold text-white">گفتگو</h3>
        <p v-if="mentorStore.messages.length === 0" class="text-sm text-slate-400">
          هنوز پیامی رد و بدل نشده است.
        </p>
        <ul v-else class="space-y-2">
          <li
            v-for="message in mentorStore.messages"
            :key="message.id"
            class="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm"
          >
            <p class="text-slate-200">{{ message.body }}</p>
            <p class="mt-1 text-xs text-slate-500">
              {{ message.sender_id === authStore.user?.id ? 'شما' : mentorStore.selectedMentor.name }}
              · {{ formatTime(message.created_at) }}
            </p>
          </li>
        </ul>

        <form class="mt-4 flex gap-2" @submit.prevent="handleSend">
          <input
            v-model="draft"
            type="text"
            class="flex-1 rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
            placeholder="پیام خود را بنویسید..."
          />
          <button
            type="submit"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
          >
            ارسال
          </button>
        </form>
      </div>

      <!-- Programs -->
      <div class="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <h3 class="mb-3 font-semibold text-white">برنامه‌ها</h3>
        <p v-if="mentorStore.programs.length === 0" class="text-sm text-slate-400">
          هنوز برنامه‌ای ارسال نشده است.
        </p>
        <ul v-else class="space-y-3">
          <li
            v-for="program in mentorStore.programs"
            :key="program.id"
            class="rounded-lg border border-slate-800 bg-slate-950/60 p-3"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h4 class="font-semibold text-white">{{ program.title }}</h4>
              <span class="rounded-md bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                {{ categoryLabel(program.category) }}
              </span>
            </div>
            <p v-if="program.description" class="mt-1 text-sm text-slate-400">
              {{ program.description }}
            </p>
            <button
              v-if="program.routine_id === null"
              type="button"
              class="mt-3 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400/70"
              @click="handleAdopt(program.id)"
            >
              افزودن به روتین‌های من
            </button>
            <p v-else class="mt-3 text-xs text-emerald-300">
              به روتین‌های شما اضافه شد.
            </p>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useMentorStore } from '@/stores/mentor';
import { useRoutineStore } from '@/stores/routine';

const authStore = useAuthStore();
const mentorStore = useMentorStore();
const routineStore = useRoutineStore();

const draft = ref('');
const errorMessage = ref('');

function formatTime(value: string): string {
  try {
    return new Date(value).toLocaleString('fa-IR');
  } catch {
    return value;
  }
}

function categoryLabel(category: string): string {
  switch (category) {
    case 'study':
      return 'درسی';
    case 'sport':
      return 'ورزشی';
    case 'life':
      return 'زندگی';
    default:
      return 'سایر';
  }
}

async function loadAll(): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorStore.fetchMentors();
    await mentorStore.fetchSelectedMentor();
    if (mentorStore.selectedMentor) {
      await mentorStore.fetchMessages(mentorStore.selectedMentor.id);
      await mentorStore.fetchPrograms();
    }
  } catch {
    errorMessage.value = 'بارگذاری اطلاعات مربی ناموفق بود.';
  }
}

async function handleSelect(mentorId: string): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorStore.selectMentor(mentorId);
    await mentorStore.fetchMessages(mentorId);
    await mentorStore.fetchPrograms();
  } catch {
    errorMessage.value = 'انتخاب مربی ناموفق بود.';
  }
}

async function handleChangeMentor(): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorStore.clearMentor();
  } catch {
    errorMessage.value = 'لغو انتخاب مربی ناموفق بود.';
  }
}

async function handleSend(): Promise<void> {
  const body = draft.value.trim();
  if (!body) {
    return;
  }
  const mentorId = mentorStore.selectedMentor?.id;
  if (!mentorId) {
    return;
  }
  errorMessage.value = '';
  try {
    await mentorStore.sendMessage(body, mentorId);
    draft.value = '';
  } catch {
    errorMessage.value = 'ارسال پیام ناموفق بود.';
  }
}

async function handleAdopt(programId: string): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorStore.adoptProgram(programId);
    await routineStore.fetchRoutines();
  } catch {
    errorMessage.value = 'افزودن برنامه به روتین‌ها ناموفق بود.';
  }
}

onMounted(() => {
  void loadAll();
});
</script>
