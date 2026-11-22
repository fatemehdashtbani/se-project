/** Shared form-validation rules and their Persian messages. */

export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const MIN_PASSWORD_LENGTH = 8;

export const EMAIL_REQUIRED_MESSAGE = 'ایمیل الزامی است';
export const EMAIL_FORMAT_MESSAGE = 'فرمت ایمیل معتبر نیست';
export const PASSWORD_LENGTH_MESSAGE = 'رمز عبور باید حداقل ۸ کاراکتر باشد';

/** Return the Persian error for an email, or null when it is acceptable. */
export function validateEmail(email: string): string | null {
  const value = email.trim();

  if (value === '') {
    return EMAIL_REQUIRED_MESSAGE;
  }

  if (!EMAIL_PATTERN.test(value)) {
    return EMAIL_FORMAT_MESSAGE;
  }

  return null;
}

/** Return the Persian error for a password, or null when it is acceptable. */
export function validatePassword(password: string): string | null {
  return password.length < MIN_PASSWORD_LENGTH ? PASSWORD_LENGTH_MESSAGE : null;
}
