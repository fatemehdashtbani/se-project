import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import fa from 'element-plus/es/locale/lang/fa';
import 'element-plus/dist/index.css';
import App from './App.vue';
import router from './router';
import { useAuthStore } from './stores/auth';
import { initTheme } from './shared/theme';
import './assets/styles/main.css';
import './assets/styles/admin.css';

initTheme();

async function bootstrap(): Promise<void> {
  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);
  app.use(ElementPlus, { locale: fa });

  // Hydrate from the HttpOnly session cookie before the first navigation;
  // otherwise the router guard would bounce a signed-in user to /login.
  await useAuthStore(pinia).init();

  app.use(router);
  await router.isReady();
  app.mount('#app');
}

void bootstrap();
