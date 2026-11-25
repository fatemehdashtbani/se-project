<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-5xl items-center px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">میز کار مربی</p>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-10 pb-24 sm:px-6">
      <p
        v-if="errorMessage"
        role="alert"
        class="mb-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
      >
        {{ errorMessage }}
      </p>

      <div class="grid gap-6 lg:grid-cols-3">
        <!-- Clients -->
        <section class="rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6">
          <h2 class="text-lg font-semibold text-white">موکل‌ها</h2>
          <p v-if="mentorStore.clients.length === 0" class="mt-4 text-sm text-slate-400">
            هنوز موکلی ندارید.
          </p>
          <ul v-else class="mt-4 space-y-2">
            <li v-for="client in mentorStore.clients" :key="client.id">
              <button
                type="button"
                class="w-full rounded-lg border px-3 py-2 text-right text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400/70"
                :class="
                  selectedClientId === client.id
                    ? 'border-blue-500/60 bg-blue-500/10 text-white'
                    : 'border-slate-700 bg-slate-900/70 text-slate-200 hover:bg-slate-800/70'
                "
                @click="selectClient(client.id)"
              >
                {{ client.name }}
              </button>
            </li>
          </ul>
        </section>

        <!-- Thread + composer -->
        <section class="rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6 lg:col-span-2">
          <h2 class="text-lg font-semibold text-white">گفتگو</h2>

          <p v-if="!selectedClientId" class="mt-4 text-sm text-slate-400">
            یک موکل را انتخاب کنید.
          </p>

          <template v-else>
            <div class="mt-4 space-y-2">
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
                    {{ message.sender_id === authStore.user?.id ? 'شما' : selectedClientName }}
                    · {{ formatTime(message.created_at) }}
                  </p>
                </li>
              </ul>
            </div>

            <form class="mt-4 flex gap-2" @submit.prevent="handleReply">
              <input
                v-model="replyDraft"
                type="text"
                class="flex-1 rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
                placeholder="پاسخ شما..."
              />
              <button
                type="submit"
                class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
              >
                ارسال
              </button>
            </form>

            <!-- Program form -->
            <div class="mt-6 rounded-xl border border-slate-700 bg-slate-900/70 p-4">
              <h3 class="mb-3 font-semibold text-white">ارسال برنامه</h3>
              <form class="space-y-3" @submit.prevent="handleSendProgram">
                <div>
                  <label class="mb-1 block text-sm font-medium text-slate-200">عنوان</label>
                  <input
                    v-model="programTitle"
                    type="text"
                    class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
                  />
                </div>
                <div>
                  <label class="mb-1 block text-sm font-medium text-slate-200">دسته‌بندی</label>
                  <select
                    v-model="programCategory"
                    class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
                  >
                    <option value="study">درسی</option>
                    <option value="sport">ورزشی</option>
                    <option value="life">زندگی</option>
                    <option value="other">سایر</option>
                  </select>
                </div>
                <div>
                  <label class="mb-1 block text-sm font-medium text-slate-200">توضیحات</label>
                  <textarea
                    v-model="programDescription"
                    rows="3"
                    class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
                  ></textarea>
                </div>
                <button
                  type="submit"
                  class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400/70"
                >
                  ارسال برنامه
                </button>
              </form>
            </div>
          </template>
        </section>
      </div>
    </main>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import BottomNav from '@/components/BottomNav.vue';
import { useAuthStore } from '@/stores/auth';
import { useMentorStore, type ProgramCategory } from '@/stores/mentor';

const authStore = useAuthStore();
const mentorStore = useMentorStore();

const selectedClientId = ref<string | null>(null);
const replyDraft = ref('');
const programTitle = ref('');
const programDescription = ref('');
const programCategory = ref<ProgramCategory>('study');
const errorMessage = ref('');

const selectedClientName = computed(() => {
  const client = mentorStore.clients.find((item) => item.id === selectedClientId.value);
  return client?.name ?? '';
});

function formatTime(value: string): string {
  try {
    return new Date(value).toLocaleString('fa-IR');
  } catch {
    return value;
  }
}

async function loadClients(): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorStore.fetchClients();
  } catch {
    errorMessage.value = 'بارگذاری موکل‌ها ناموفق بود.';
  }
}

async function selectClient(clientId: string): Promise<void> {
  selectedClientId.value = clientId;
  errorMessage.value = '';
  try {
    await mentorStore.fetchMessages(undefined, clientId);
    await mentorStore.fetchPrograms(clientId);
  } catch {
    errorMessage.value = 'بارگذاری گفتگو ناموفق بود.';
  }
}

async function handleReply(): Promise<void> {
  const body = replyDraft.value.trim();
  if (!body || !selectedClientId.value) {
    return;
  }
  errorMessage.value = '';
  try {
    await mentorStore.sendMessage(body, undefined, selectedClientId.value);
    replyDraft.value = '';
  } catch {
    errorMessage.value = 'ارسال پیام ناموفق بود.';
  }
}

async function handleSendProgram(): Promise<void> {
  const title = programTitle.value.trim();
  if (!title || !selectedClientId.value) {
    return;
  }
  errorMessage.value = '';
  try {
    await mentorStore.sendProgram({
      clientId: selectedClientId.value,
      title,
      description: programDescription.value.trim() || null,
      category: programCategory.value,
    });
    programTitle.value = '';
    programDescription.value = '';
  } catch {
    errorMessage.value = 'ارسال برنامه ناموفق بود.';
  }
}

onMounted(() => {
  void loadClients();
});
</script>
