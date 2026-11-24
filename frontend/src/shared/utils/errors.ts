/** Persian, user-facing messages for stable backend error codes. */

const MESSAGES: Record<string, string> = {
  INVALID_CREDENTIALS: 'ایمیل یا رمز عبور نادرست است',
  INVALID_CURRENT_PASSWORD: 'رمز عبور فعلی نادرست است',
  VALIDATION_ERROR: 'اطلاعات وارد شده معتبر نیست',
  EMAIL_ALREADY_EXISTS: 'این ایمیل قبلاً ثبت شده است',
  USERNAME_ALREADY_EXISTS: 'این نام کاربری قبلاً انتخاب شده است',
  INVALID_RESET_TOKEN: 'لینک بازیابی رمز نامعتبر است یا منقضی شده است',
  EMAIL_DELIVERY_FAILED: 'ارسال ایمیل بازیابی ممکن نشد. لطفاً دوباره تلاش کنید',
  EMAIL_NOT_CONFIGURED: 'ارسال ایمیل بازیابی روی سرور فعال نیست. با پشتیبانی تماس بگیرید',
  RATE_LIMITED: 'تعداد درخواست‌ها زیاد است. کمی بعد دوباره تلاش کنید',
};

const FALLBACK = 'خطایی رخ داد. لطفاً دوباره تلاش کنید';

export function getPersianError(code: string): string {
  return MESSAGES[code] ?? FALLBACK;
}
