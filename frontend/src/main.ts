import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useAuthStore } from './stores/auth';
import './assets/styles/main.css';

async function bootstrap(): Promise<void> {
  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);

  // Hydrate from the HttpOnly session cookie before the first navigation;
  // otherwise the router guard would bounce a signed-in user to /login.
  await useAuthStore(pinia).init();

  app.use(router);
  await router.isReady();
  app.mount('#app');
}

void bootstrap();
