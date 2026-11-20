import { describe, expect, it } from 'vitest';
import { getPersianError } from '../errors';

describe('getPersianError (F-023)', () => {
  it('maps INVALID_CREDENTIALS to a Persian message', () => {
    expect(getPersianError('INVALID_CREDENTIALS')).toBe('ایمیل یا رمز عبور نادرست است');
  });

  it('maps VALIDATION_ERROR to a Persian message', () => {
    expect(getPersianError('VALIDATION_ERROR')).toBe('اطلاعات وارد شده معتبر نیست');
  });

  it('falls back to a generic Persian message for unknown codes', () => {
    expect(getPersianError('SOMETHING_UNEXPECTED')).toBe(
      'خطایی رخ داد. لطفاً دوباره تلاش کنید',
    );
  });
});
