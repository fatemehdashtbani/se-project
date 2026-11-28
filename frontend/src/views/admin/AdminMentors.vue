<template>
  <section class="space-y-4">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-extrabold text-violet-900">منتورها و منتورشیپ</h2>
        <p class="mt-1 text-sm admin-muted">
          تایید درخواست‌ها، مدیریت منتورهای فعال و نظارت بر گفتگوها.
        </p>
      </div>
      <el-button type="primary" plain @click="openAssign">
        <el-icon class="ml-1"><Plus /></el-icon>
        اختصاص منتور به کاربر
      </el-button>
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
        <el-tab-pane label="درخواست‌های منتور شدن" name="applications">
          <el-table
            v-loading="applicationStore.isLoading"
            :data="applicationStore.applications"
            row-key="id"
          >
            <el-table-column label="متقاضی" min-width="200">
              <template #default="{ row }">
                <p class="font-bold text-violet-900">{{ row.applicant_name }}</p>
                <p dir="ltr" class="text-left text-xs admin-muted">
                  {{ row.applicant_email }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="حوزه تخصص" min-width="160" prop="expertise" />

            <el-table-column label="رزومه و سوابق" min-width="260">
              <template #default="{ row }">
                <p class="whitespace-pre-line text-xs leading-6">
                  {{ row.bio }}
                </p>
                <p
                  v-if="row.documents"
                  class="mt-1 whitespace-pre-line break-words text-xs text-violet-500"
                >
                  {{ row.documents }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="وضعیت" width="110">
              <template #default="{ row }">
                <el-tag :type="applicationTagType(row.status)" effect="light">
                  {{ applicationStatusLabels[row.status as MentorApplicationStatus] }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="تاریخ" width="130">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>

            <el-table-column label="عملیات" width="180">
              <template #default="{ row }">
                <div v-if="row.status === 'pending'" class="flex gap-1">
                  <el-button
                    size="small"
                    type="success"
                    :disabled="applicationStore.isLoading"
                    @click="approve(row.id)"
                  >
                    تایید
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    plain
                    :disabled="applicationStore.isLoading"
                    @click="reject(row.id)"
                  >
                    رد
                  </el-button>
                </div>
                <span v-else class="text-xs admin-muted">بررسی شده</span>
              </template>
            </el-table-column>

            <template #empty>
              <p class="admin-empty">درخواستی در انتظار بررسی وجود ندارد.</p>
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="منتورهای فعال" name="mentors">
          <el-table
            v-loading="adminStore.isLoading"
            :data="adminStore.mentors"
            row-key="id"
          >
            <el-table-column label="منتور" min-width="220">
              <template #default="{ row }">
                <p class="font-bold text-violet-900">{{ row.name }}</p>
                <p dir="ltr" class="text-left text-xs admin-muted">{{ row.email }}</p>
              </template>
            </el-table-column>

            <el-table-column label="معرفی" min-width="260">
              <template #default="{ row }">
                <p class="text-sm">{{ row.headline || '—' }}</p>
                <p class="mt-1 line-clamp-2 text-xs admin-muted">
                  {{ row.bio || '' }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="کاربران" width="110" align="center">
              <template #default="{ row }">
                <el-tag effect="plain">{{ toPersianDigits(row.clients_count) }}</el-tag>
              </template>
            </el-table-column>

            <el-table-column label="تاریخ عضویت" width="140">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>

            <el-table-column label="عملیات" width="150">
              <template #default="{ row }">
                <el-button size="small" type="danger" plain @click="remove(row.id, row.name)">
                  حذف منتور
                </el-button>
              </template>
            </el-table-column>

            <template #empty>
              <p class="admin-empty">هنوز منتوری تایید نشده است.</p>
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="گزارش گفتگوها" name="conversations">
          <el-table
            v-loading="adminStore.isLoading"
            :data="adminStore.conversations"
            :row-key="(row: ConversationSummary) => `${row.user_id}-${row.mentor_id}`"
          >
            <el-table-column label="کاربر" min-width="200">
              <template #default="{ row }">
                <p class="font-bold text-violet-900">{{ row.user_name }}</p>
                <p dir="ltr" class="text-left text-xs admin-muted">
                  {{ row.user_email }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="منتور" min-width="200">
              <template #default="{ row }">
                <p class="font-bold text-violet-900">{{ row.mentor_name }}</p>
                <p dir="ltr" class="text-left text-xs admin-muted">
                  {{ row.mentor_email }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="تعداد پیام" width="110" align="center">
              <template #default="{ row }">
                {{ toPersianDigits(row.messages_count) }}
              </template>
            </el-table-column>

            <el-table-column label="آخرین پیام" width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.last_message_at) }}
              </template>
            </el-table-column>

            <el-table-column label="عملیات" width="140">
              <template #default="{ row }">
                <el-button size="small" plain @click="openThread(row)">مشاهده</el-button>
              </template>
            </el-table-column>

            <template #empty>
              <p class="admin-empty">هنوز گفتگویی بین منتور و کاربر ثبت نشده است.</p>
            </template>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="assignDialog" title="اختصاص منتور به کاربر" width="460">
      <el-form label-position="top">
        <el-form-item label="کاربر">
          <el-select v-model="assignUserId" placeholder="یک کاربر انتخاب کنید" filterable>
            <el-option
              v-for="user in assignableUsers"
              :key="user.id"
              :label="`${user.email} — ${user.username ?? ''}`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="منتور">
          <el-select v-model="assignMentorId" placeholder="یک منتور انتخاب کنید" filterable>
            <el-option
              v-for="mentor in adminStore.mentors"
              :key="mentor.id"
              :label="`${mentor.name} — ${mentor.email}`"
              :value="mentor.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="assignDialog = false">انصراف</el-button>
        <el-button
          type="primary"
          :disabled="!assignUserId || !assignMentorId"
          :loading="assigning"
          @click="submitAssign"
        >
          اختصاص بده
        </el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="threadDrawer" title="گزارش گفتگو" size="520px">
      <p class="mb-4 text-sm admin-muted">
        {{ threadTitle }}
      </p>
      <el-skeleton v-if="threadLoading" :rows="5" animated />
      <div v-else-if="threadMessages.length === 0" class="admin-empty">
        پیامی در این گفتگو ثبت نشده است.
      </div>
      <ul v-else class="space-y-3">
        <li
          v-for="message in threadMessages"
          :key="message.id"
          class="rounded-xl border border-violet-100 p-3"
        >
          <div class="flex items-center justify-between gap-2">
            <span class="text-sm font-bold text-violet-800">
              {{ message.sender_name }}
            </span>
            <span class="text-xs admin-muted">
              {{ formatDateTime(message.created_at) }}
            </span>
          </div>
          <p class="mt-2 whitespace-pre-line text-sm leading-7">{{ message.body }}</p>
        </li>
      </ul>
    </el-drawer>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { apiRequest } from '@/shared/api/client';
import { formatDate, formatDateTime, toPersianDigits } from '@/shared/utils/format';
import {
  applicationStatusLabels,
  useMentorApplicationStore,
  type MentorApplicationStatus,
} from '@/stores/mentorApplication';
import {
  useAdminStore,
  type AdminMessage,
  type AdminUser,
  type ConversationSummary,
} from '@/stores/admin';

const adminStore = useAdminStore();
const applicationStore = useMentorApplicationStore();

const activeTab = ref<'applications' | 'mentors' | 'conversations'>('applications');
const errorMessage = ref('');

const assignDialog = ref(false);
const assignUserId = ref('');
const assignMentorId = ref('');
const assignableUsers = ref<AdminUser[]>([]);
const assigning = ref(false);

const threadDrawer = ref(false);
const threadLoading = ref(false);
const threadMessages = ref<AdminMessage[]>([]);
const threadTitle = ref('');

function applicationTagType(
  status: string,
): 'warning' | 'success' | 'danger' {
  if (status === 'approved') {
    return 'success';
  }
  return status === 'rejected' ? 'danger' : 'warning';
}

async function loadApplications(): Promise<void> {
  errorMessage.value = '';
  try {
    await applicationStore.fetchApplications();
  } catch {
    errorMessage.value = 'بارگذاری درخواست‌های منتور شدن ناموفق بود.';
  }
}

async function approve(applicationId: string): Promise<void> {
  try {
    await applicationStore.approve(applicationId);
    ElMessage.success('درخواست تایید شد و نقش حساب به منتور تغییر کرد.');
    await Promise.all([loadApplications(), adminStore.fetchMentors()]);
  } catch {
    ElMessage.error('تایید درخواست ناموفق بود.');
  }
}

async function reject(applicationId: string): Promise<void> {
  try {
    await ElMessageBox.confirm(
      'این درخواست رد می‌شود. کاربر می‌تواند بعداً درخواست جدیدی ثبت کند.',
      'رد درخواست',
      { confirmButtonText: 'رد کن', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  try {
    await applicationStore.reject(applicationId);
    ElMessage.success('درخواست رد شد.');
    await loadApplications();
  } catch {
    ElMessage.error('رد درخواست ناموفق بود.');
  }
}

async function remove(mentorId: string, name: string): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `«${name}» از نقش منتور خارج می‌شود و منتورشیپ‌های فعال او پایان می‌یابد.`,
      'حذف منتور',
      { confirmButtonText: 'حذف کن', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  try {
    await adminStore.removeMentor(mentorId);
    ElMessage.success('منتور حذف شد.');
    await adminStore.fetchMentors();
  } catch {
    ElMessage.error('حذف منتور ناموفق بود.');
  }
}

async function openAssign(): Promise<void> {
  assignUserId.value = '';
  assignMentorId.value = '';
  assignDialog.value = true;
  try {
    const response = await apiRequest<{ items: AdminUser[] }>(
      '/api/v1/admin/users?role=user&limit=100',
    );
    assignableUsers.value = response.items;
  } catch {
    ElMessage.error('بارگذاری فهرست کاربران ناموفق بود.');
  }
}

async function submitAssign(): Promise<void> {
  assigning.value = true;
  try {
    await adminStore.assignMentor(assignUserId.value, assignMentorId.value);
    ElMessage.success('منتور به کاربر اختصاص داده شد.');
    assignDialog.value = false;
    await adminStore.fetchMentors();
  } catch {
    ElMessage.error('اختصاص منتور ناموفق بود.');
  } finally {
    assigning.value = false;
  }
}

async function openThread(conversation: ConversationSummary): Promise<void> {
  threadDrawer.value = true;
  threadLoading.value = true;
  threadMessages.value = [];
  threadTitle.value = `${conversation.user_name} ↔ ${conversation.mentor_name}`;

  try {
    threadMessages.value = await adminStore.fetchConversationMessages(
      conversation.user_id,
      conversation.mentor_id,
    );
  } catch {
    ElMessage.error('بارگذاری پیام‌های گفتگو ناموفق بود.');
  } finally {
    threadLoading.value = false;
  }
}

onMounted(() => {
  void loadApplications();
  void adminStore.fetchMentors();
  void adminStore.fetchConversations();
});
</script>
