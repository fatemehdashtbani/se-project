<template>
  <section class="space-y-4">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-extrabold text-violet-900">سیستم و لاگ‌ها</h2>
        <p class="mt-1 text-sm admin-muted">
          ارسال اعلان سراسری و بررسی خطاها و رفتارهای مشکوک سامانه.
        </p>
      </div>
    </div>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
    />

    <el-card class="admin-card" shadow="never">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="اعلان سراسری" name="broadcast">
          <div class="grid gap-6 lg:grid-cols-2">
            <el-form label-position="top">
              <el-form-item label="عنوان اعلان" required>
                <el-input
                  v-model="broadcastTitle"
                  maxlength="200"
                  show-word-limit
                  placeholder="مثلاً به‌روزرسانی فردا"
                />
              </el-form-item>
              <el-form-item label="متن پیام" required>
                <el-input
                  v-model="broadcastBody"
                  type="textarea"
                  :rows="5"
                  maxlength="5000"
                  show-word-limit
                  placeholder="اپلیکیشن فردا به‌روزرسانی می‌شود."
                />
              </el-form-item>
              <el-button
                type="primary"
                :loading="sending"
                :disabled="!broadcastTitle.trim() || !broadcastBody.trim()"
                @click="sendBroadcast"
              >
                <el-icon class="ml-1"><Promotion /></el-icon>
                ارسال به همه کاربران
              </el-button>
              <p class="mt-3 text-xs admin-muted">
                اعلان برای همه حساب‌های فعال سامانه ثبت و در فهرست زیر نگهداری می‌شود.
              </p>
            </el-form>

            <div>
              <p class="mb-2 text-sm font-bold text-violet-800">اعلان‌های ارسال‌شده</p>
              <div
                v-if="adminStore.broadcasts.length === 0"
                class="admin-empty rounded-xl border border-dashed border-violet-200"
              >
                هنوز اعلانی ارسال نشده است.
              </div>
              <ul v-else class="space-y-3">
                <li
                  v-for="broadcast in adminStore.broadcasts"
                  :key="broadcast.id"
                  class="rounded-xl border border-violet-100 p-3"
                >
                  <div class="flex items-start justify-between gap-2">
                    <div class="min-w-0">
                      <p class="font-bold text-violet-900">{{ broadcast.title }}</p>
                      <p class="mt-1 whitespace-pre-line text-sm leading-6">
                        {{ broadcast.body }}
                      </p>
                    </div>
                    <el-button
                      size="small"
                      type="danger"
                      text
                      @click="removeBroadcast(broadcast.id, broadcast.title)"
                    >
                      حذف
                    </el-button>
                  </div>
                  <div class="mt-2 flex flex-wrap gap-3 text-xs admin-muted">
                    <span>{{ formatDateTime(broadcast.created_at) }}</span>
                    <span>
                      {{ toPersianDigits(broadcast.recipients) }} گیرنده
                    </span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="لاگ سیستم" name="logs">
          <div class="mb-4 flex flex-wrap items-end gap-3">
            <el-select v-model="logLevel" placeholder="همه سطوح" clearable class="w-40">
              <el-option label="خطا" value="error" />
              <el-option label="هشدار" value="warning" />
              <el-option label="اطلاع" value="info" />
              <el-option label="اقدام مدیریتی" value="audit" />
            </el-select>
            <el-input
              v-model="logSearch"
              placeholder="جستجو در پیام یا مسیر"
              clearable
              class="max-w-xs"
              @keyup.enter="loadLogs"
              @clear="loadLogs"
            />
            <el-button :loading="adminStore.isLoading" @click="loadLogs">
              اعمال فیلتر
            </el-button>
            <el-tag effect="plain" round>
              {{ toPersianDigits(adminStore.logsTotal) }} رکورد
            </el-tag>
          </div>

          <el-table v-loading="adminStore.isLoading" :data="adminStore.logs" row-key="id">
            <el-table-column label="سطح" width="120">
              <template #default="{ row }">
                <el-tag :type="levelTagType(row.level)" effect="light">
                  {{ levelLabels[row.level as LogLevel] }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="رویداد" width="180">
              <template #default="{ row }">
                <span dir="ltr" class="inline-block text-xs">{{ row.event }}</span>
              </template>
            </el-table-column>

            <el-table-column label="پیام" min-width="300">
              <template #default="{ row }">
                <p class="break-words text-sm">{{ row.message }}</p>
                <p
                  v-if="row.path"
                  dir="ltr"
                  class="mt-1 text-left text-xs admin-muted"
                >
                  {{ row.method }} {{ row.path }} — {{ row.status_code }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="زمان" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>

            <template #empty>
              <p class="admin-empty">رکوردی با این فیلترها وجود ندارد.</p>
            </template>
          </el-table>

          <div class="mt-4 flex justify-center">
            <el-pagination
              v-model:current-page="logPage"
              :page-size="logPageSize"
              :total="adminStore.logsTotal"
              layout="prev, pager, next"
              background
              @current-change="loadLogs"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Promotion } from '@element-plus/icons-vue';
import { formatDateTime, toPersianDigits } from '@/shared/utils/format';
import { useAdminStore } from '@/stores/admin';

type LogLevel = 'error' | 'warning' | 'info' | 'audit';

const adminStore = useAdminStore();

const activeTab = ref<'broadcast' | 'logs'>('broadcast');
const errorMessage = ref('');

const broadcastTitle = ref('');
const broadcastBody = ref('');
const sending = ref(false);

const logLevel = ref('');
const logSearch = ref('');
const logPage = ref(1);
const logPageSize = 20;

const levelLabels: Record<LogLevel, string> = {
  error: 'خطا',
  warning: 'هشدار',
  info: 'اطلاع',
  audit: 'اقدام مدیریتی',
};

function levelTagType(level: LogLevel): 'danger' | 'warning' | 'info' | 'success' {
  switch (level) {
    case 'error':
      return 'danger';
    case 'warning':
      return 'warning';
    case 'audit':
      return 'success';
    default:
      return 'info';
  }
}

async function sendBroadcast(): Promise<void> {
  sending.value = true;
  try {
    await adminStore.createBroadcast(
      broadcastTitle.value.trim(),
      broadcastBody.value.trim(),
    );
    ElMessage.success('اعلان برای همه کاربران ثبت شد.');
    broadcastTitle.value = '';
    broadcastBody.value = '';
    await adminStore.fetchBroadcasts();
  } catch {
    ElMessage.error('ارسال اعلان ناموفق بود.');
  } finally {
    sending.value = false;
  }
}

async function removeBroadcast(id: string, title: string): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `اعلان «${title}» حذف شود؟`,
      'حذف اعلان',
      { confirmButtonText: 'حذف کن', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  try {
    await adminStore.deleteBroadcast(id);
    ElMessage.success('اعلان حذف شد.');
    await adminStore.fetchBroadcasts();
  } catch {
    ElMessage.error('حذف اعلان ناموفق بود.');
  }
}

async function loadLogs(): Promise<void> {
  errorMessage.value = '';
  try {
    await adminStore.fetchLogs(
      logLevel.value,
      logSearch.value,
      (logPage.value - 1) * logPageSize,
      logPageSize,
    );
  } catch {
    errorMessage.value = 'بارگذاری لاگ سیستم ناموفق بود.';
  }
}

onMounted(async () => {
  try {
    await Promise.all([adminStore.fetchBroadcasts(), loadLogs()]);
  } catch {
    errorMessage.value = 'بارگذاری اطلاعات سیستم ناموفق بود.';
  }
});
</script>
