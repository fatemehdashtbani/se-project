<template>
  <section class="space-y-4">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-extrabold text-violet-900">محتوا و روتین‌ها</h2>
        <p class="mt-1 text-sm admin-muted">
          قالب‌های آماده روتین و دسته‌بندی عادت‌ها را مدیریت کنید.
        </p>
      </div>
      <el-button type="primary" @click="openTemplateDialog()">
        <el-icon class="ml-1"><Plus /></el-icon>
        قالب جدید
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
        <el-tab-pane label="قالب‌های آماده" name="templates">
          <el-table
            v-loading="adminStore.isLoading"
            :data="adminStore.templates"
            row-key="id"
          >
            <el-table-column label="عنوان" min-width="200">
              <template #default="{ row }">
                <p class="font-bold text-violet-900">{{ row.title }}</p>
                <p class="mt-1 line-clamp-2 text-xs admin-muted">
                  {{ row.description || '—' }}
                </p>
              </template>
            </el-table-column>

            <el-table-column label="دسته‌بندی" width="140">
              <template #default="{ row }">
                <el-tag v-if="row.category" effect="plain">{{ row.category }}</el-tag>
                <span v-else class="text-xs admin-muted">—</span>
              </template>
            </el-table-column>

            <el-table-column label="مدت" width="110" align="center">
              <template #default="{ row }">
                {{ row.duration_days ? `${toPersianDigits(row.duration_days)} روز` : '—' }}
              </template>
            </el-table-column>

            <el-table-column label="انتشار" width="110">
              <template #default="{ row }">
                <el-tag :type="row.is_published ? 'success' : 'info'" effect="light">
                  {{ row.is_published ? 'منتشر شده' : 'پیش‌نویس' }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="تاریخ ایجاد" width="140">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>

            <el-table-column label="عملیات" width="160">
              <template #default="{ row }">
                <div class="flex gap-1">
                  <el-button size="small" plain @click="openTemplateDialog(row)">
                    ویرایش
                  </el-button>
                  <el-button size="small" type="danger" plain @click="removeTemplate(row)">
                    حذف
                  </el-button>
                </div>
              </template>
            </el-table-column>

            <template #empty>
              <p class="admin-empty">هنوز قالبی ساخته نشده است.</p>
            </template>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="دسته‌بندی عادت‌ها" name="categories">
          <div class="mb-4 flex justify-end">
            <el-button type="primary" plain @click="openCategoryDialog()">
              <el-icon class="ml-1"><Plus /></el-icon>
              دسته‌بندی جدید
            </el-button>
          </div>

          <el-table
            v-loading="adminStore.isLoading"
            :data="adminStore.categories"
            row-key="id"
          >
            <el-table-column label="نام" min-width="180">
              <template #default="{ row }">
                <div class="flex items-center gap-2">
                  <span
                    class="inline-block h-4 w-4 rounded-full border border-violet-200"
                    :style="{ backgroundColor: row.color }"
                  />
                  <span class="font-bold text-violet-900">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="توضیح" min-width="240">
              <template #default="{ row }">
                <span class="text-sm">{{ row.description || '—' }}</span>
              </template>
            </el-table-column>

            <el-table-column label="رنگ" width="120">
              <template #default="{ row }">
                <span dir="ltr" class="text-xs admin-muted">{{ row.color }}</span>
              </template>
            </el-table-column>

            <el-table-column label="عملیات" width="160">
              <template #default="{ row }">
                <div class="flex gap-1">
                  <el-button size="small" plain @click="openCategoryDialog(row)">
                    ویرایش
                  </el-button>
                  <el-button size="small" type="danger" plain @click="removeCategory(row)">
                    حذف
                  </el-button>
                </div>
              </template>
            </el-table-column>

            <template #empty>
              <p class="admin-empty">هنوز دسته‌بندی‌ای تعریف نشده است.</p>
            </template>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog
      v-model="templateDialog"
      :title="editingTemplateId ? 'ویرایش قالب' : 'قالب روتین جدید'"
      width="520"
    >
      <el-form label-position="top">
        <el-form-item label="عنوان" required>
          <el-input v-model="templateForm.title" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="توضیح">
          <el-input
            v-model="templateForm.description"
            type="textarea"
            :rows="4"
            placeholder="مثلاً برنامه ورزشی ۳۰ روزه با تمرکز بر تمرین‌های خانگی"
          />
        </el-form-item>
        <div class="grid gap-4 sm:grid-cols-2">
          <el-form-item label="دسته‌بندی">
            <el-select v-model="templateForm.category" clearable placeholder="انتخاب کنید">
              <el-option
                v-for="category in adminStore.categories"
                :key="category.id"
                :label="category.name"
                :value="category.name"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="مدت (روز)">
            <el-input-number
              v-model="templateForm.duration_days"
              :min="1"
              :max="365"
              class="w-full"
            />
          </el-form-item>
        </div>
        <el-form-item label="انتشار برای کاربران">
          <el-switch v-model="templateForm.is_published" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="templateDialog = false">انصراف</el-button>
        <el-button
          type="primary"
          :loading="saving"
          :disabled="!templateForm.title.trim()"
          @click="saveTemplate"
        >
          ذخیره
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="categoryDialog"
      :title="editingCategoryId ? 'ویرایش دسته‌بندی' : 'دسته‌بندی جدید'"
      width="460"
    >
      <el-form label-position="top">
        <el-form-item label="نام" required>
          <el-input v-model="categoryForm.name" maxlength="60" />
        </el-form-item>
        <el-form-item label="توضیح">
          <el-input v-model="categoryForm.description" maxlength="255" />
        </el-form-item>
        <el-form-item label="رنگ">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="categoryDialog = false">انصراف</el-button>
        <el-button
          type="primary"
          :loading="saving"
          :disabled="!categoryForm.name.trim()"
          @click="saveCategory"
        >
          ذخیره
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { formatDate, toPersianDigits } from '@/shared/utils/format';
import {
  useAdminStore,
  type HabitCategory,
  type RoutineTemplate,
} from '@/stores/admin';

const adminStore = useAdminStore();

const activeTab = ref<'templates' | 'categories'>('templates');
const errorMessage = ref('');
const saving = ref(false);

const templateDialog = ref(false);
const editingTemplateId = ref<string | null>(null);
const templateForm = reactive({
  title: '',
  description: '',
  category: '',
  duration_days: null as number | null,
  is_published: true,
});

const categoryDialog = ref(false);
const editingCategoryId = ref<string | null>(null);
const categoryForm = reactive({
  name: '',
  description: '',
  color: '#7c3aed',
});

function openTemplateDialog(template?: RoutineTemplate): void {
  editingTemplateId.value = template?.id ?? null;
  templateForm.title = template?.title ?? '';
  templateForm.description = template?.description ?? '';
  templateForm.category = template?.category ?? '';
  templateForm.duration_days = template?.duration_days ?? null;
  templateForm.is_published = template?.is_published ?? true;
  templateDialog.value = true;
}

async function saveTemplate(): Promise<void> {
  if (!templateForm.title.trim()) {
    ElMessage.warning('عنوان قالب را وارد کنید.');
    return;
  }

  saving.value = true;
  const payload = {
    title: templateForm.title.trim(),
    description: templateForm.description.trim() || null,
    category: templateForm.category || null,
    duration_days: templateForm.duration_days,
    is_published: templateForm.is_published,
  };

  try {
    if (editingTemplateId.value) {
      await adminStore.updateTemplate(editingTemplateId.value, payload);
      ElMessage.success('قالب به‌روزرسانی شد.');
    } else {
      await adminStore.createTemplate(payload);
      ElMessage.success('قالب ساخته شد.');
    }
    templateDialog.value = false;
    await adminStore.fetchTemplates();
  } catch {
    ElMessage.error('ذخیره قالب ناموفق بود.');
  } finally {
    saving.value = false;
  }
}

async function removeTemplate(template: RoutineTemplate): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `قالب «${template.title}» حذف می‌شود.`,
      'حذف قالب',
      { confirmButtonText: 'حذف کن', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  try {
    await adminStore.deleteTemplate(template.id);
    ElMessage.success('قالب حذف شد.');
    await adminStore.fetchTemplates();
  } catch {
    ElMessage.error('حذف قالب ناموفق بود.');
  }
}

function openCategoryDialog(category?: HabitCategory): void {
  editingCategoryId.value = category?.id ?? null;
  categoryForm.name = category?.name ?? '';
  categoryForm.description = category?.description ?? '';
  categoryForm.color = category?.color ?? '#7c3aed';
  categoryDialog.value = true;
}

async function saveCategory(): Promise<void> {
  if (!categoryForm.name.trim()) {
    ElMessage.warning('نام دسته‌بندی را وارد کنید.');
    return;
  }

  saving.value = true;
  const payload = {
    name: categoryForm.name.trim(),
    description: categoryForm.description.trim() || null,
    color: categoryForm.color,
  };

  try {
    if (editingCategoryId.value) {
      await adminStore.updateCategory(editingCategoryId.value, payload);
      ElMessage.success('دسته‌بندی به‌روزرسانی شد.');
    } else {
      await adminStore.createCategory(payload);
      ElMessage.success('دسته‌بندی ایجاد شد.');
    }
    categoryDialog.value = false;
    await adminStore.fetchCategories();
  } catch {
    ElMessage.error('ذخیره دسته‌بندی ناموفق بود.');
  } finally {
    saving.value = false;
  }
}

async function removeCategory(category: HabitCategory): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `دسته‌بندی «${category.name}» حذف می‌شود.`,
      'حذف دسته‌بندی',
      { confirmButtonText: 'حذف کن', cancelButtonText: 'انصراف', type: 'warning' },
    );
  } catch {
    return;
  }

  try {
    await adminStore.deleteCategory(category.id);
    ElMessage.success('دسته‌بندی حذف شد.');
    await adminStore.fetchCategories();
  } catch {
    ElMessage.error('حذف دسته‌بندی ناموفق بود.');
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      adminStore.fetchTemplates(),
      adminStore.fetchCategories(),
    ]);
  } catch {
    errorMessage.value = 'بارگذاری محتوای مدیریتی ناموفق بود.';
  }
});
</script>
