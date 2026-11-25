<template>
  <div dir="rtl" class="min-h-screen bg-slate-900 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
        <p class="text-xl font-extrabold tracking-tight text-white sm:text-2xl">روتین کده</p>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-4 py-10 pb-24 sm:px-6">
      <h1 class="text-2xl font-bold text-white">تقویم</h1>
      <p class="mt-2 text-sm text-slate-400">رویدادهای هر روز را ببین و برای روزهای بعد یادداشت بگذار.</p>

      <form
        class="mt-6 flex flex-col gap-3 rounded-xl border border-slate-700 bg-slate-800/40 p-4 sm:flex-row sm:items-end"
        @submit.prevent="handleCreate"
      >
        <div class="flex-1">
          <label for="event-new-title" class="mb-1 block text-sm font-medium text-slate-200">
            عنوان رویداد
          </label>
          <input
            id="event-new-title"
            v-model="newTitle"
            type="text"
            placeholder="مثلاً جلسه ورزش"
            class="w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/60"
          />
        </div>
        <div>
          <p class="mb-1 block text-sm font-medium text-slate-200">تاریخ</p>
          <p
            class="rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white"
            aria-live="polite"
          >
            {{ selectedDateLabel }}
          </p>
        </div>
        <button
          type="submit"
          class="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/70"
        >
          افزودن
        </button>
      </form>
      <p class="mt-2 text-xs text-slate-500">برای تغییر تاریخ، روز مورد نظر را در تقویم انتخاب کنید.</p>

      <p
        v-if="errorMessage"
        role="alert"
        class="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200"
      >
        {{ errorMessage }}
      </p>

      <section class="mt-8 rounded-2xl border border-slate-800 bg-slate-800/40 p-4 sm:p-5">
        <div class="flex items-center justify-between gap-2">
          <button
            type="button"
            aria-label="ماه بعد"
            class="rounded-md border border-slate-600 px-2.5 py-1.5 text-sm text-slate-300 transition-colors hover:bg-slate-700/50 focus:outline-none focus:ring-2 focus:ring-slate-400/60"
            @click="nextMonth"
          >
            ›
          </button>
          <div class="flex items-center gap-3">
            <p class="text-base font-semibold text-white">{{ monthName }}</p>
            <button
              type="button"
              class="rounded-md border border-slate-600 px-2 py-1 text-xs text-slate-300 transition-colors hover:bg-slate-700/50 focus:outline-none focus:ring-2 focus:ring-slate-400/60"
              @click="goToToday"
            >
              امروز
            </button>
          </div>
          <button
            type="button"
            aria-label="ماه قبل"
            class="rounded-md border border-slate-600 px-2.5 py-1.5 text-sm text-slate-300 transition-colors hover:bg-slate-700/50 focus:outline-none focus:ring-2 focus:ring-slate-400/60"
            @click="previousMonth"
          >
            ‹
          </button>
        </div>

        <div class="mt-4 grid grid-cols-7 gap-1 text-center text-xs text-slate-400">
          <span v-for="weekday in PERSIAN_WEEKDAYS" :key="weekday">{{ weekday }}</span>
        </div>

        <div class="mt-2 grid grid-cols-7 gap-1">
          <template v-for="(day, index) in cells" :key="index">
            <div v-if="day === null" class="min-h-[64px]"></div>
            <button
              v-else
              type="button"
              :aria-label="`${dayLabel(day)} ${monthName}`"
              class="min-h-[64px] rounded-lg border p-1.5 text-right transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/60"
              :class="cellClass(day)"
              @click="selectDay(day)"
            >
              <span class="text-xs">{{ dayLabel(day) }}</span>
              <span
                v-if="eventsForDay(day).length > 0"
                class="mt-1 block h-1.5 w-1.5 rounded-full bg-blue-400"
                :title="`${toPersianDigits(eventsForDay(day).length)} رویداد`"
              ></span>
            </button>
          </template>
        </div>
      </section>

      <section class="mt-8">
        <h2 class="text-xl font-semibold text-white">رویدادهای این ماه</h2>

        <p v-if="monthEvents.length === 0" class="mt-3 text-sm text-slate-400">
          برای این ماه رویدادی ثبت نشده است
        </p>

        <ul v-else class="mt-4 space-y-3">
          <li
            v-for="event in monthEvents"
            :key="event.id"
            class="flex items-center gap-3 rounded-xl border border-slate-700 bg-slate-800/40 px-4 py-3"
          >
            <span class="w-24 shrink-0 text-xs text-slate-400">{{ formatJalaliDate(event.event_date) }}</span>
            <span class="flex-1 text-sm text-slate-100">{{ event.title }}</span>
            <button
              type="button"
              class="rounded-md border border-red-500/50 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-500/10 focus:outline-none focus:ring-2 focus:ring-red-400/60"
              @click="handleDelete(event.id)"
            >
              حذف
            </button>
          </li>
        </ul>
      </section>
    </main>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import BottomNav from '@/components/BottomNav.vue';
import { useCalendarStore, type CalendarEvent } from '@/stores/calendar';
import {
  PERSIAN_WEEKDAYS,
  buildMonthCells,
  formatJalaliDate,
  jalaliDateKey,
  jalaliFromKey,
  monthLabel,
  toPersianDigits,
  todayJalali,
  todayKey,
} from '@/shared/utils/calendar';

const calendarStore = useCalendarStore();

const start = todayJalali();
const viewYear = ref(start.jy);
// Jalali months are 1-based in the helpers; keep the same convention here.
const viewMonth = ref(start.jm);
const newTitle = ref('');
const newEventDate = ref(todayKey());
const errorMessage = ref('');

const today = todayKey();
const cells = computed(() => buildMonthCells(viewYear.value, viewMonth.value));
const monthName = computed(() => monthLabel(viewYear.value, viewMonth.value));
const selectedDateLabel = computed(() => formatJalaliDate(newEventDate.value));

const eventsByDate = computed(() => {
  const map = new Map<string, CalendarEvent[]>();
  for (const event of calendarStore.events) {
    const list = map.get(event.event_date) ?? [];
    list.push(event);
    map.set(event.event_date, list);
  }
  return map;
});

const monthEvents = computed(() =>
  calendarStore.events.filter((event) => {
    const { jy, jm } = jalaliFromKey(event.event_date);
    return jy === viewYear.value && jm === viewMonth.value;
  }),
);

function dayLabel(day: number | null): string {
  return day === null ? '' : toPersianDigits(day);
}

function eventsForDay(day: number | null): CalendarEvent[] {
  if (day === null) {
    return [];
  }
  return eventsByDate.value.get(jalaliDateKey(viewYear.value, viewMonth.value, day)) ?? [];
}

function cellClass(day: number | null): string {
  if (day === null) {
    return '';
  }

  const key = jalaliDateKey(viewYear.value, viewMonth.value, day);

  if (key === today) {
    return 'border-blue-400 bg-blue-500/10';
  }
  if (key === newEventDate.value) {
    return 'border-slate-500 bg-slate-700/60';
  }
  return 'border-slate-700 bg-slate-900/60 hover:bg-slate-700/40';
}

function selectDay(day: number | null): void {
  if (day === null) {
    return;
  }
  newEventDate.value = jalaliDateKey(viewYear.value, viewMonth.value, day);
}

function previousMonth(): void {
  if (viewMonth.value === 1) {
    viewMonth.value = 12;
    viewYear.value -= 1;
    return;
  }
  viewMonth.value -= 1;
}

function nextMonth(): void {
  if (viewMonth.value === 12) {
    viewMonth.value = 1;
    viewYear.value += 1;
    return;
  }
  viewMonth.value += 1;
}

function goToToday(): void {
  const current = todayJalali();
  viewYear.value = current.jy;
  viewMonth.value = current.jm;
  newEventDate.value = todayKey();
}

async function loadEvents(): Promise<void> {
  try {
    await calendarStore.fetchEvents();
  } catch {
    errorMessage.value = 'بارگذاری تقویم ناموفق بود.';
  }
}

onMounted(() => {
  void loadEvents();
});

async function handleCreate(): Promise<void> {
  const title = newTitle.value.trim();

  if (!title) {
    errorMessage.value = 'عنوان رویداد الزامی است.';
    return;
  }

  if (!newEventDate.value) {
    errorMessage.value = 'تاریخ رویداد الزامی است.';
    return;
  }

  try {
    await calendarStore.createEvent(title, newEventDate.value);
    newTitle.value = '';
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'ذخیره رویداد ناموفق بود.';
  }
}

async function handleDelete(id: string): Promise<void> {
  try {
    await calendarStore.deleteEvent(id);
    errorMessage.value = '';
  } catch {
    errorMessage.value = 'حذف رویداد ناموفق بود.';
  }
}
</script>
