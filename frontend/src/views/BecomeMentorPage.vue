<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-3xl items-center px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">
          درخواست همکاری به عنوان مربی
        </p>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-10 pb-24 sm:px-6">
      <p
        v-if="errorMessage"
        role="alert"
        class="mb-5 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200"
      >
        {{ errorMessage }}
      </p>

      <p
        v-if="successMessage"
        role="status"
        class="mb-5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200"
      >
        {{ successMessage }}
      </p>

      <section
        v-if="isMentor"
        class="rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6"
      >
        <h2 class="text-lg font-semibold text-white">شما مربی هستید</h2>
        <p class="mt-2 text-sm text-slate-400">
          حساب شما نقش مربی دارد و نیازی به ارسال درخواست همکاری نیست.
        </p>
        <RouterLink
          to="/mentor"
          class="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
        >
          میز کار مربی
        </RouterLink>
      </section>

      <template v-else>
        <section
          v-if="mentorApplicationStore.application?.status === 'pending'"
          class="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-5 sm:p-6"
        >
          <h2 class="text-lg font-semibold text-amber-200">درخواست شما در انتظار تایید است</h2>
          <p class="mt-2 text-sm text-amber-100/80">
            اطلاعات شما ثبت شد. پس از بررسی توسط مدیر، نتیجه از همین صفحه قابل مشاهده است.
          </p>
          <p class="mt-3 text-sm text-amber-100/80">
            <span class="font-medium">تخصص:</span> {{ mentorApplicationStore.application.expertise }}
          </p>
        </section>

        <p
          v-else-if="mentorApplicationStore.application?.status === 'rejected'"
          class="mb-5 rounded-xl border border-slate-700 bg-slate-800/60 px-4 py-3 text-sm text-slate-300"
        >
          درخواست قبلی شما تایید نشد. می‌توانید اطلاعات را اصلاح کنید و دوباره ارسال کنید.
        </p>

        <p
          v-else-if="mentorApplicationStore.application?.status === 'approved'"
          class="mb-5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200"
        >
          درخواست شما تایید شده است.
        </p>

        <form
          v-if="showForm"
          class="space-y-5 rounded-2xl border border-slate-800 bg-slate-800/40 p-5 sm:p-6"
          novalidate
          @submit.prevent="handleSubmit"
        >
          <p class="text-sm text-slate-400">
            برای فعالیت به عنوان مربی، تخصص، بیوگرافی و مدارک خود را وارد کنید. درخواست شما پس از
            ثبت در وضعیت «در انتظار تایید» قرار می‌گیرد.
          </p>

          <div>
            <label for="expertise" class="mb-2 block text-sm text-slate-300">
              حوزه تخصص
            </label>
            <input
              id="expertise"
              v-model="expertise"
              type="text"
              maxlength="200"
              placeholder="مثلاً برنامه‌ریزی درسی و مطالعه"
              class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              :aria-invalid="errors.expertise ? 'true' : 'false'"
              :aria-describedby="errors.expertise ? 'expertise-error' : undefined"
            />
            <p
              v-if="errors.expertise"
              id="expertise-error"
              role="alert"
              class="mt-2 text-sm text-rose-300"
            >
              {{ errors.expertise }}
            </p>
          </div>

          <div>
            <label for="bio" class="mb-2 block text-sm text-slate-300">بیوگرافی</label>
            <textarea
              id="bio"
              v-model="bio"
              rows="4"
              maxlength="5000"
              placeholder="تجربه، سابقه و رویکرد خود را بنویسید."
              class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              :aria-invalid="errors.bio ? 'true' : 'false'"
              :aria-describedby="errors.bio ? 'bio-error' : undefined"
            ></textarea>
            <p v-if="errors.bio" id="bio-error" role="alert" class="mt-2 text-sm text-rose-300">
              {{ errors.bio }}
            </p>
          </div>

          <div>
            <label for="documents" class="mb-2 block text-sm text-slate-300">
              مدارک و سوابق
            </label>
            <textarea
              id="documents"
              v-model="documents"
              rows="3"
              maxlength="2000"
              placeholder="لینک مدارک یا توضیح سوابق (اختیاری)"
              class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            ></textarea>
          </div>

          <button
            type="submit"
            :disabled="mentorApplicationStore.isLoading"
            class="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/60 disabled:cursor-not-allowed disabled:opacity-60"
          >
            ارسال درخواست
          </button>
        </form>
      </template>
    </main>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import BottomNav from '@/components/BottomNav.vue';
import { useAuthStore } from '@/stores/auth';
import { useMentorApplicationStore } from '@/stores/mentorApplication';

const authStore = useAuthStore();
const mentorApplicationStore = useMentorApplicationStore();

const expertise = ref('');
const bio = ref('');
const documents = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const errors = reactive({ expertise: '', bio: '' });

const isMentor = computed(() => authStore.user?.role === 'mentor');

// A pending request cannot be edited: the administrator is already reviewing
// the submitted details. Rejected and fresh applications can be filled in.
const showForm = computed(
  () =>
    mentorApplicationStore.application?.status !== 'pending' &&
    mentorApplicationStore.application?.status !== 'approved',
);

function hydrateForm(): void {
  const application = mentorApplicationStore.application;
  if (!application) {
    return;
  }
  expertise.value = application.expertise;
  bio.value = application.bio;
  documents.value = application.documents ?? '';
}

async function loadApplication(): Promise<void> {
  errorMessage.value = '';
  try {
    await mentorApplicationStore.fetchMine();
    hydrateForm();
  } catch {
    errorMessage.value = 'بارگذاری وضعیت درخواست ناموفق بود.';
  }
}

function validate(): boolean {
  errors.expertise = expertise.value.trim() ? '' : 'حوزه تخصص الزامی است.';
  errors.bio = bio.value.trim() ? '' : 'بیوگرافی الزامی است.';
  return errors.expertise === '' && errors.bio === '';
}

async function handleSubmit(): Promise<void> {
  successMessage.value = '';
  if (!validate()) {
    return;
  }

  errorMessage.value = '';
  try {
    await mentorApplicationStore.submit({
      expertise: expertise.value.trim(),
      bio: bio.value.trim(),
      documents: documents.value.trim() || null,
    });
    successMessage.value = 'درخواست شما ثبت شد و در انتظار تایید مدیر است.';
  } catch {
    errorMessage.value = 'ثبت درخواست ناموفق بود. دوباره تلاش کنید.';
  }
}

onMounted(() => {
  void loadApplication();
});
</script>
