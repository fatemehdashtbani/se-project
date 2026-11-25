import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '@/views/LoginPage.vue';
import DashboardPage from '@/views/DashboardPage.vue';
import AdminLayout from '@/components/AdminLayout.vue';
import AdminHome from '@/views/admin/AdminHome.vue';
import AdminSectionPage from '@/views/admin/AdminSectionPage.vue';
import ForbiddenPage from '@/views/ForbiddenPage.vue';
import { useAuthStore, type UserRole } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: LoginPage },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/checklist',
      name: 'checklist',
      component: () => import('@/views/ChecklistPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/notes',
      name: 'notes',
      component: () => import('@/views/NotesPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mentor',
      name: 'mentor',
      component: () => import('@/views/MentorPage.vue'),
      meta: { requiresAuth: true, requiresRole: 'mentor' as UserRole },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterPage.vue'),
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/ForgotPasswordPage.vue'),
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('@/views/ResetPasswordPage.vue'),
    },
    {
      path: '/forbidden',
      name: 'forbidden',
      component: ForbiddenPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresRole: 'admin' as UserRole },
      children: [
        { path: '', name: 'admin', component: AdminHome },
        {
          path: 'users',
          name: 'admin-users',
          component: AdminSectionPage,
          meta: { title: 'مدیریت کاربران' },
        },
        {
          path: 'plans',
          name: 'admin-plans',
          component: AdminSectionPage,
          meta: { title: 'مدیریت اشتراکها' },
        },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.user) {
    return '/login';
  }

  // Navigation-only guard. Every admin operation must still be authorised by
  // the server; the browser session's role is never trusted as proof.
  const requiredRole = to.meta.requiresRole as UserRole | undefined;
  if (requiredRole && auth.user?.role !== requiredRole) {
    return { name: 'forbidden', query: { required: requiredRole } };
  }

  return true;
});

export default router;
