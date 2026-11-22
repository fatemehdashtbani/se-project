import { defineConfig, devices } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const BACKEND_URL = 'http://127.0.0.1:8000';

/**
 * End-to-end suite for the browser journeys.
 *
 * Both servers are started by Playwright: the backend with a dedicated
 * `e2e.db` (mirrored in `../backend/.env.e2e`) and migrations applied first,
 * and Vite on 5173 so `/api` stays same-origin and the session cookie works.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: BASE_URL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // The Playwright CDN answers 403 ("not available in your location")
        // from this network, so the bundled browser cannot be downloaded.
        // The installed Google Chrome is used instead.
        channel: 'chrome',
      },
    },
  ],
  webServer: [
    {
      command:
        '.venv\\Scripts\\alembic.exe upgrade head && ' +
        '.venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8000',
      cwd: '../backend',
      env: { DATABASE_URL: 'sqlite+aiosqlite:///./e2e.db' },
      url: `${BACKEND_URL}/healthz`,
      reuseExistingServer: false,
      timeout: 120_000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      command: 'npm run dev -- --port 5173',
      url: BASE_URL,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
