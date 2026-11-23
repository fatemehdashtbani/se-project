/** Persian, user-facing messages for stable backend error codes. */

const MESSAGES: Record<string, string> = {
  INVALID_CREDENTIALS: 'ایمیل یا رمز عبور نادرست است',
  VALIDATION_ERROR: 'اطلاعات وارد شده معتبر نیست',
  EMAIL_ALREADY_EXISTS: 'این ایمیل قبلاً ثبت شده است',
  USERNAME_ALREADY_EXISTS: 'این نام کاربری قبلاً انتخاب شده است',
};

const FALLBACK = 'خطایی رخ داد. لطفاً دوباره تلاش کنید';

export function getPersianError(code: string): string {
  return MESSAGES[code] ?? FALLBACK;
}
