/** Shared form-validation rules and their Persian messages. */

export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const MIN_PASSWORD_LENGTH = 8;

export const EMAIL_REQUIRED_MESSAGE = 'ایمیل الزامی است';
export const EMAIL_FORMAT_MESSAGE = 'فرمت ایمیل معتبر نیست';
export const PASSWORD_LENGTH_MESSAGE = 'رمز عبور باید حداقل ۸ کاراکتر باشد';
export const FIRST_NAME_REQUIRED_MESSAGE = 'نام الزامی است';
export const LAST_NAME_REQUIRED_MESSAGE = 'نام خانوادگی الزامی است';
export const USERNAME_REQUIRED_MESSAGE = 'نام کاربری الزامی است';
export const USERNAME_FORMAT_MESSAGE =
  'نام کاربری باید ۳ تا ۵۰ کاراکتر و بدون فاصله باشد';
export const PHONE_REQUIRED_MESSAGE = 'شماره تلفن الزامی است';
export const PHONE_FORMAT_MESSAGE = 'شماره تلفن معتبر نیست';

const USERNAME_PATTERN = /^\S{3,50}$/;
const PHONE_PATTERN = /^\+?[0-9]{7,15}$/;

/** Return the supplied message for a blank value, or null when it is filled. */
export function validateRequired(value: string, message: string): string | null {
  return value.trim() === '' ? message : null;
}

/** Strip the spaces and dashes people type into phone fields. */
export function normalizePhone(value: string): string {
  return value.replace(/[\s-]/g, '');
}

/** Return the Persian error for a username, or null when it is acceptable. */
export function validateUsername(value: string): string | null {
  const username = value.trim();

  if (username === '') {
    return USERNAME_REQUIRED_MESSAGE;
  }

  return USERNAME_PATTERN.test(username) ? null : USERNAME_FORMAT_MESSAGE;
}

/** Return the Persian error for a phone number, or null when it is acceptable. */
export function validatePhone(value: string): string | null {
  const phone = normalizePhone(value);

  if (phone === '') {
    return PHONE_REQUIRED_MESSAGE;
  }

  return PHONE_PATTERN.test(phone) ? null : PHONE_FORMAT_MESSAGE;
}

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
