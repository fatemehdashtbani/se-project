<template>
  <div
    v-if="visible"
    dir="rtl"
    class="fixed inset-x-0 bottom-20 z-40 mx-auto max-w-xl px-3"
    aria-live="polite"
  >
    <div class="rounded-xl border border-blue-500/40 bg-slate-800 p-4 shadow-lg">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0 flex-1">
          <p class="text-sm font-bold text-white">رویدادهای امروز</p>
          <ul class="mt-2 space-y-1 text-sm text-slate-200">
            <li
              v-for="event in todayEvents"
              :key="event.id"
              class="flex flex-wrap items-center gap-2"
            >
              <span
                v-if="event.event_time"
                class="shrink-0 rounded bg-slate-700 px-1.5 py-0.5 text-xs text-blue-200"
              >
                {{ formatEventTime(event.event_time) }}
              </span>
              <span class="min-w-0 break-words">{{ event.title }}</span>
            </li>
          </ul>
          <button
            v-if="canAskPermission"
            type="button"
            class="mt-3 rounded-md border border-blue-500/50 px-3 py-1.5 text-xs font-medium text-blue-300 transition-colors hover:bg-blue-500/10 focus:outline-none focus:ring-2 focus:ring-blue-400/60"
            @click="enableBrowserNotifications"
          >
            فعال کردن اعلان مرورگر
          </button>
        </div>
        <button
          type="button"
          aria-label="بستن اعلان رویدادهای امروز"
          class="shrink-0 rounded-md border border-slate-600 px-2 py-1 text-xs text-slate-300 transition-colors hover:bg-slate-700/50 focus:outline-none focus:ring-2 focus:ring-slate-400/60"
          @click="dismissToday"
        >
          بستن
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useCalendarStore, type CalendarEvent } from '@/stores/calendar';
import { formatEventTime, todayKey } from '@/shared/utils/calendar';

/** Remembers the day whose banner the user closed (F-034). */
const DISMISSED_KEY = 'routine-kade-today-reminders-dismissed';
/** Remembers which set of events was already announced in a browser notification. */
const ANNOUNCED_KEY = 'routine-kade-today-announced';

const authStore = useAuthStore();
const calendarStore = useCalendarStore();

const notificationSupported = typeof window !== 'undefined' && 'Notification' in window;
const permission = ref<NotificationPermission | 'unsupported'>(
  notificationSupported ? Notification.permission : 'unsupported',
);
const today = ref(todayKey());
const dismissed = ref(false);
const timers: ReturnType<typeof setTimeout>[] = [];

const todayEvents = computed<CalendarEvent[]>(() =>
  calendarStore.events
    .filter((event) => event.event_date === today.value)
    .slice()
    .sort(
      (a, b) =>
        (a.event_time ?? '').localeCompare(b.event_time ?? '') ||
        a.title.localeCompare(b.title),
    ),
);

const visible = computed(
  () => Boolean(authStore.user) && !dismissed.value && todayEvents.value.length > 0,
);

const canAskPermission = computed(() => permission.value === 'default');

function readDismissal(): void {
  dismissed.value = localStorage.getItem(DISMISSED_KEY) === today.value;
}

function dismissToday(): void {
  dismissed.value = true;
  localStorage.setItem(DISMISSED_KEY, today.value);
}

function describe(event: CalendarEvent): string {
  const time = formatEventTime(event.event_time);
  return time ? `${time} ${event.title}` : event.title;
}

function pushNotification(title: string, body: string): void {
  if (!notificationSupported || Notification.permission !== 'granted') {
    return;
  }

  try {
    void new Notification(title, { body });
  } catch {
    // Some browsers only allow notifications from a service worker; the
    // in-app banner still covers the reminder.
  }
}

/** One notification per day and per set of events, so a reload is quiet. */
function announceToday(): void {
  if (todayEvents.value.length === 0) {
    return;
  }

  const key = `${today.value}:${todayEvents.value.map((event) => event.id).join(',')}`;
  if (localStorage.getItem(ANNOUNCED_KEY) === key) {
    return;
  }

  pushNotification('رویدادهای امروز', todayEvents.value.map(describe).join('، '));
  localStorage.setItem(ANNOUNCED_KEY, key);
}

function clearTimers(): void {
  while (timers.length > 0) {
    clearTimeout(timers.pop());
  }
}

/** Notify again when an event's time arrives while the app stays open. */
function scheduleTimedNotifications(): void {
  clearTimers();

  const now = new Date();
  for (const event of todayEvents.value) {
    if (!event.event_time) {
      continue;
    }

    const [hours = '0', minutes = '0'] = event.event_time.split(':');
    const at = new Date(now);
    at.setHours(Number(hours), Number(minutes), 0, 0);

    const delay = at.getTime() - now.getTime();
    if (delay <= 0 || delay > 24 * 60 * 60 * 1000) {
      continue;
    }

    timers.push(
      setTimeout(() => {
        pushNotification('رویداد امروز', describe(event));
      }, delay),
    );
  }
}

async function loadToday(): Promise<void> {
  today.value = todayKey();
  readDismissal();

  if (!authStore.user) {
    return;
  }

  if (calendarStore.events.length === 0) {
    try {
      await calendarStore.fetchEvents();
    } catch {
      // A failed reminder must never block the page.
      return;
    }
  }

  announceToday();
  scheduleTimedNotifications();
}

async function enableBrowserNotifications(): Promise<void> {
  if (!notificationSupported) {
    return;
  }

  permission.value = await Notification.requestPermission();

  if (permission.value === 'granted') {
    announceToday();
    scheduleTimedNotifications();
  }
}

watch(
  () => authStore.user,
  (user) => {
    if (user) {
      void loadToday();
    }
  },
);

onMounted(() => {
  void loadToday();
});

onBeforeUnmount(clearTimers);
</script>
