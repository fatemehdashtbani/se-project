import { expect, test } from '@playwright/test';

const PASSWORD = 'secret123';
const SUCCESS_MESSAGE = 'منطقه زمانی با موفقیت ذخیره شد';

test('register, update the timezone, and log out', async ({ page }) => {
  const stamp = Date.now();
  const email = `e2e-${stamp}@example.com`;
  const username = `e2e_${stamp}`;

  // 1-4: create the account through the real form.
  await page.goto('/register');
  await page.locator('#register-first-name').fill('سارا');
  await page.locator('#register-last-name').fill('احمدی');
  await page.locator('#register-username').fill(username);
  await page.locator('#register-phone').fill('09121234567');
  await page.locator('#register-email').fill(email);
  await page.locator('#register-password').fill(PASSWORD);
  await page.locator('#register-confirm-password').fill(PASSWORD);
  await page.locator('button[type="submit"]').click();

  // 5-6: auto-login lands on the dashboard, where the bottom navigation
  // carries the profile link (the top bar holds no account controls).
  await expect(page).toHaveURL(/\/dashboard$/);
  const profileLink = page.getByRole('link', { name: 'پروفایل' });
  await expect(profileLink).toBeVisible();

  // 7-8: the profile page shows the new account's email.
  await profileLink.click();
  await expect(page).toHaveURL(/\/profile$/);
  await expect(page.getByText(email)).toBeVisible();

  // 9-10: the profile form writes to the database, not just the view.
  await page.locator('#profile-first-name').fill('سارا');
  await page.locator('#profile-last-name').fill('احمدی');
  await page.locator('#profile-phone').fill('09121234567');
  await page.locator('#profile-form button[type="submit"]').click();
  await expect(page.getByRole('status')).toHaveText('اطلاعات با موفقیت ذخیره شد');

  // 11-12: changing the zone reports success.
  await page.locator('#timezone').selectOption('Asia/Tehran');
  await page.locator('#timezone-form button[type="submit"]').click();
  await expect(page.getByRole('status')).toHaveText(SUCCESS_MESSAGE);

  // Both values must survive a full reload, i.e. they were persisted
  // server-side and the boot-time `init()` hydration works with a real cookie.
  await page.reload();
  await expect(page.locator('#timezone')).toHaveValue('Asia/Tehran');
  await expect(page.locator('#profile-first-name')).toHaveValue('سارا');
  await expect(page.locator('#profile-last-name')).toHaveValue('احمدی');
  await expect(page).toHaveURL(/\/profile$/);

  // 13-14: back to the dashboard, then log out.
  await page.goBack();
  await expect(page).toHaveURL(/\/dashboard$/);
  await page.getByRole('button', { name: 'خروج' }).click();
  await expect(page).toHaveURL(/\/login$/);

  // The session is really gone: the guard bounces /dashboard.
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login$/);
});
