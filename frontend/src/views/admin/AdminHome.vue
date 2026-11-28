<template>
  <section class="space-y-6">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-extrabold text-violet-900">نمای کلی سامانه</h2>
        <p class="mt-1 text-sm admin-muted">
          آمار کاربران، روتین‌ها، منتورها و فعالیت روزانه در یک نگاه.
        </p>
      </div>
      <el-button :loading="adminStore.isLoading" @click="load">
        <el-icon class="ml-1"><Refresh /></el-icon>
        به‌روزرسانی
      </el-button>
    </div>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
    />

    <el-skeleton v-if="!dashboard && adminStore.isLoading" :rows="6" animated />

    <template v-else-if="dashboard">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="card in cards" :key="card.label" class="admin-stat">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm admin-muted">{{ card.label }}</p>
              <p class="mt-2 text-3xl font-extrabold text-violet-900">
                {{ toPersianDigits(card.value) }}
              </p>
            </div>
            <span class="admin-stat__icon">
              <el-icon :size="20"><component :is="card.icon" /></el-icon>
            </span>
          </div>
          <p class="mt-3 text-xs text-violet-500">{{ card.note }}</p>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-3">
        <el-card class="admin-card lg:col-span-2" shadow="never">
          <template #header>
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span>فعالیت ۱۴ روز گذشته</span>
              <div class="flex items-center gap-4 text-xs font-medium">
                <span class="flex items-center gap-1">
                  <span class="inline-block h-2.5 w-2.5 rounded-sm bg-violet-600" />
                  کاربران فعال
                </span>
                <span class="flex items-center gap-1">
                  <span class="inline-block h-2.5 w-2.5 rounded-sm bg-violet-400" />
                  روتین جدید
                </span>
                <span class="flex items-center gap-1">
                  <span class="inline-block h-2.5 w-2.5 rounded-sm bg-violet-200" />
                  ثبت‌نام
                </span>
              </div>
            </div>
          </template>

          <div class="flex h-56 items-end gap-2" dir="ltr">
            <el-tooltip
              v-for="point in dashboard.activity"
              :key="point.date"
              placement="top"
              :content="`${formatDayLabel(point.date)} — فعال: ${toPersianDigits(
                point.active_users,
              )}، روتین: ${toPersianDigits(point.routines)}، ثبت‌نام: ${toPersianDigits(
                point.signups,
              )}`"
            >
              <div class="flex h-full flex-1 flex-col justify-end">
                <div class="flex h-full items-end justify-center gap-1">
                  <div
                    class="w-2.5 rounded-t bg-violet-600 transition-all"
                    :style="{ height: barHeight(point.active_users) }"
                  />
                  <div
                    class="w-2.5 rounded-t bg-violet-400 transition-all"
                    :style="{ height: barHeight(point.routines) }"
                  />
                  <div
                    class="w-2.5 rounded-t bg-violet-200 transition-all"
                    :style="{ height: barHeight(point.signups) }"
                  />
                </div>
                <p class="mt-2 text-center text-[10px] text-violet-400">
                  {{ formatDayLabel(point.date) }}
                </p>
              </div>
            </el-tooltip>
          </div>
        </el-card>

        <el-card class="admin-card" shadow="never">
          <template #header>امروز</template>
          <ul class="space-y-4 text-sm">
            <li class="flex items-center justify-between gap-2">
              <span class="admin-muted">کاربران فعال امروز</span>
              <span class="text-lg font-extrabold text-violet-800">
                {{ toPersianDigits(dashboard.active_today) }}
              </span>
            </li>
            <li class="flex items-center justify-between gap-2">
              <span class="admin-muted">منتورشیپ‌های فعال</span>
              <span class="text-lg font-extrabold text-violet-800">
                {{ toPersianDigits(dashboard.active_mentorships) }}
              </span>
            </li>
            <li class="flex items-center justify-between gap-2">
              <span class="admin-muted">برنامه‌های ارسالی منتورها</span>
              <span class="text-lg font-extrabold text-violet-800">
                {{ toPersianDigits(dashboard.total_mentor_programs) }}
              </span>
            </li>
            <li class="flex items-center justify-between gap-2">
              <span class="admin-muted">قالب‌های آماده</span>
              <span class="text-lg font-extrabold text-violet-800">
                {{ toPersianDigits(dashboard.total_templates) }}
              </span>
            </li>
            <li class="flex items-center justify-between gap-2">
              <span class="admin-muted">دسته‌بندی عادت‌ها</span>
              <span class="text-lg font-extrabold text-violet-800">
                {{ toPersianDigits(dashboard.total_categories) }}
              </span>
            </li>
            <li class="flex items-center justify-between gap-2">
              <span class="admin-muted">اعلان‌های سراسری</span>
              <span class="text-lg font-extrabold text-violet-800">
                {{ toPersianDigits(dashboard.total_broadcasts) }}
              </span>
            </li>
          </ul>

          <el-divider />

          <div class="space-y-2">
            <el-button class="w-full" type="primary" plain @click="go('/admin/mentors')">
              بررسی درخواست‌های منتور شدن
            </el-button>
            <el-button class="w-full" plain @click="go('/admin/content')">
              مدیریت قالب‌ها و دسته‌بندی‌ها
            </el-button>
            <el-button class="w-full" plain @click="go('/admin/system')">
              ارسال اعلان سراسری
            </el-button>
          </div>
        </el-card>
      </div>

      <el-alert
        v-if="dashboard.banned_users > 0"
        :title="`${toPersianDigits(dashboard.banned_users)} حساب مسدود شده است.`"
        type="warning"
        show-icon
        :closable="false"
      />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import {
  ChatLineSquare,
  Collection,
  Refresh,
  User,
  UserFilled,
} from '@element-plus/icons-vue';
import { formatDayLabel, toPersianDigits } from '@/shared/utils/format';
import { useAdminStore } from '@/stores/admin';

const adminStore = useAdminStore();
const router = useRouter();
const errorMessage = ref('');

const dashboard = computed(() => adminStore.dashboard);

const cards = computed(() => {
  const data = dashboard.value;
  if (!data) {
    return [];
  }
  return [
    {
      label: 'کل کاربران',
      value: data.total_users,
      note: `${toPersianDigits(data.active_users)} حساب فعال`,
      icon: User,
    },
    {
      label: 'روتین‌ها',
      value: data.total_routines,
      note: 'روتین‌های ایجادشده توسط کاربران',
      icon: Collection,
    },
    {
      label: 'منتورها',
      value: data.total_mentors,
      note: `${toPersianDigits(data.active_mentorships)} منتورشیپ فعال`,
      icon: UserFilled,
    },
    {
      label: 'درخواست‌های منتور شدن',
      value: data.pending_mentor_requests,
      note: 'در انتظار بررسی',
      icon: ChatLineSquare,
    },
  ];
});

const maxValue = computed(() => {
  const points = dashboard.value?.activity ?? [];
  return Math.max(
    1,
    ...points.map((point) =>
      Math.max(point.active_users, point.routines, point.signups),
    ),
  );
});

function barHeight(value: number): string {
  return `${Math.round((value / maxValue.value) * 100)}%`;
}

async function load(): Promise<void> {
  errorMessage.value = '';
  try {
    await adminStore.fetchDashboard();
  } catch {
    errorMessage.value = 'بارگذاری آمار داشبورد ناموفق بود.';
  }
}

function go(path: string): void {
  void router.push(path);
}

onMounted(() => {
  void load();
});
</script>
