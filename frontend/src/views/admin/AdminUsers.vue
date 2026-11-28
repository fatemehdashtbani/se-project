<template>
  <section class="space-y-4">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-extrabold text-violet-900">مدیریت کاربران</h2>
        <p class="mt-1 text-sm admin-muted">
          جستجو، فیلتر و اعمال محدودیت روی حساب‌های کاربران.
        </p>
      </div>
      <el-tag effect="plain" round>
        {{ toPersianDigits(adminStore.usersTotal) }} حساب
      </el-tag>
    </div>

    <el-card class="admin-card" shadow="never">
      <div class="flex flex-wrap items-end gap-3">
        <el-input
          v-model="search"
          placeholder="جستجو با ایمیل، نام یا نام کاربری"
          clearable
          class="max-w-xs"
          @keyup.enter="applyFilters"
          @clear="applyFilters"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="role" placeholder="نقش" clearable class="w-40">
          <el-option label="کاربر" value="user" />
          <el-option label="منتور" value="mentor" />
          <el-option label="مدیر" value="admin" />
        </el-select>

        <el-select v-model="status" placeholder="وضعیت" clearable class="w-40">
          <el-option label="فعال" value="active" />
          <el-option label="غیرفعال" value="disabled" />
          <el-option label="مسدود" value="banned" />
        </el-select>

        <el-button type="primary" :loading="adminStore.isLoading" @click="applyFilters">
          اعمال فیلتر
        </el-button>
      </div>
    </el-card>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
    />

    <el-card class="admin-card" shadow="never">
      <el-table
        v-loading="adminStore.isLoading"
        :data="adminStore.users"
        row-key="id"
        stripe
      >
        <el-table-column label="کاربر" min-width="220">
          <template #default="{ row }">
            <div class="min-w-0">
              <p class="truncate font-bold text-violet-900">{{ displayName(row) }}</p>
              <p dir="ltr" class="truncate text-left text-xs admin-muted">
                {{ row.email }}
              </p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="نقش" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" effect="light">
              {{ roleLabels[row.role as 'user' | 'mentor' | 'admin'] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="تاریخ عضویت" width="150">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>

        <el-table-column label="روتین‌ها" width="100" align="center">
          <template #default="{ row }">
            {{ toPersianDigits(row.routines_count) }}
          </template>
        </el-table-column>

        <el-table-column label="وضعیت" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row)" effect="plain">
              {{ statusLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="عملیات" min-width="260">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-button
                v-if="row.role !== 'admin'"
                size="small"
                :type="row.is_banned ? 'success' : 'danger'"
                plain
                :disabled="busyId === row.id"
                @click="toggleBan(row)"
              >
                {{ row.is_banned ? 'رفع مسدودی' : 'مسدود کردن' }}
              </el-button>

              <el-button
                v-if="row.role !== 'admin'"
                size="small"
                :type="row.is_active ? 'warning' : 'success'"
                plain
                :disabled="busyId === row.id"
                @click="toggleActive(row)"
              >
                {{ row.is_active ? 'غیرفعال کردن' : 'فعال کردن' }}
              </el-button>

              <el-button
                size="small"
                plain
                :disabled="busyId === row.id || row.role === 'admin'"
                @click="resetPassword(row)"
              >
                ریست رمز
              </el-button>
            </div>
          </template>
        </el-table-column>

        <template #empty>
          <p class="admin-empty">کاربری با این فیلترها پیدا نشد.</p>
        </template>
      </el-table>

      <div class="mt-4 flex justify-center">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="adminStore.usersTotal"
          layout="prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { formatDate, toPersianDigits } from '@/shared/utils/format';
import { roleLabels } from '@/shared/utils/paths';
import { useAdminStore, type AdminUser } from '@/stores/admin';

const adminStore = useAdminStore();

const search = ref('');
const role = ref('');
const status = ref('');
const page = ref(1);
const pageSize = 20;
const busyId = ref<string | null>(null);
const errorMessage = ref('');

const roleTagType = (value: AdminUser['role']) =>
  value === 'admin' ? 'danger' : value === 'mentor' ? 'success' : 'info';

function displayName(user: AdminUser): string {
  const parts = [user.first_name, user.last_name].filter(Boolean);
  if (parts.length > 0) {
    return parts.join(' ');
  }
  return user.username ?? user.email.split('@')[0];
}

function statusLabel(user: AdminUser): string {
  if (user.is_banned) {
    return 'مسدود';
  }
  return user.is_active ? 'فعال' : 'غیرفعال';
}

function statusTagType(user: AdminUser): 'danger' | 'success' | 'info' {
  if (user.is_banned) {
    return 'danger';
  }
  return user.is_active ? 'success' : 'info';
}

async function load(): Promise<void> {
  errorMessage.value = '';
  try {
    await adminStore.fetchUsers({
      search: search.value || undefined,
      role: role.value || undefined,
      status: status.value || undefined,
      limit: pageSize,
      offset: (page.value - 1) * pageSize,
    });
  } catch {
    errorMessage.value = 'بارگذاری فهرست کاربران ناموفق بود.';
  }
}

function applyFilters(): void {
  page.value = 1;
  void load();
}

async function toggleBan(user: AdminUser): Promise<void> {
  const banning = !user.is_banned;
  try {
    await ElMessageBox.confirm(
      banning
        ? 'این حساب مسدود می‌شود و تمام نشست‌های فعال آن پایان می‌یابد. ادامه می‌دهید؟'
        : 'مسدودی این حساب برداشته می‌شود. ادامه می‌دهید؟',
      banning ? 'مسدود کردن حساب' : 'رفع مسدودی',
      { confirmButtonText: 'تایید', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  busyId.value = user.id;
  try {
    await adminStore.setUserBanned(user.id, banning);
    ElMessage.success(banning ? 'حساب مسدود شد.' : 'مسدودی حساب برداشته شد.');
    await load();
  } catch {
    ElMessage.error('تغییر وضعیت مسدودی ناموفق بود.');
  } finally {
    busyId.value = null;
  }
}

async function toggleActive(user: AdminUser): Promise<void> {
  const activating = !user.is_active;
  busyId.value = user.id;
  try {
    await adminStore.setUserActive(user.id, activating);
    ElMessage.success(activating ? 'حساب فعال شد.' : 'حساب غیرفعال شد.');
    await load();
  } catch {
    ElMessage.error('تغییر وضعیت حساب ناموفق بود.');
  } finally {
    busyId.value = null;
  }
}

async function resetPassword(user: AdminUser): Promise<void> {
  try {
    await ElMessageBox.confirm(
      'رمز عبور این کاربر با یک رمز موقت جایگزین می‌شود و نشست‌های فعلی او پایان می‌یابد.',
      'ریست رمز عبور',
      { confirmButtonText: 'ریست کن', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  busyId.value = user.id;
  try {
    const temporaryPassword = await adminStore.resetUserPassword(user.id);
    await ElMessageBox.alert(
      `رمز موقت: ${temporaryPassword} — این رمز فقط یک بار نمایش داده می‌شود؛ آن را به کاربر اطلاع دهید.`,
      'رمز عبور موقت',
      { confirmButtonText: 'متوجه شدم' },
    );
  } catch {
    ElMessage.error('ریست رمز عبور ناموفق بود.');
  } finally {
    busyId.value = null;
  }
}

onMounted(() => {
  void load();
});
</script>
