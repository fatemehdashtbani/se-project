import { describe, expect, it } from 'vitest';
import {
  FIRST_NAME_REQUIRED_MESSAGE,
  USERNAME_FORMAT_MESSAGE,
  USERNAME_REQUIRED_MESSAGE,
  PHONE_FORMAT_MESSAGE,
  PHONE_REQUIRED_MESSAGE,
  validatePhone,
  validateRequired,
  validateUsername,
} from '../validation';

describe('validateUsername', () => {
  it('accepts a plain username', () => {
    expect(validateUsername('sara_ahmadi')).toBeNull();
  });

  it('requires a value', () => {
    expect(validateUsername('   ')).toBe(USERNAME_REQUIRED_MESSAGE);
  });

  it('rejects usernames shorter than three characters', () => {
    expect(validateUsername('ab')).toBe(USERNAME_FORMAT_MESSAGE);
  });

  it('rejects embedded whitespace', () => {
    expect(validateUsername('sara ahmadi')).toBe(USERNAME_FORMAT_MESSAGE);
  });
});

describe('validatePhone', () => {
  it('accepts a national number written with spaces', () => {
    expect(validatePhone('0912 345 6789')).toBeNull();
  });

  it('accepts an international prefix', () => {
    expect(validatePhone('+989121234567')).toBeNull();
  });

  it('requires a value', () => {
    expect(validatePhone('   ')).toBe(PHONE_REQUIRED_MESSAGE);
  });

  it('rejects a value that is not a phone number', () => {
    expect(validatePhone('not-a-phone')).toBe(PHONE_FORMAT_MESSAGE);
  });
});

describe('validateRequired', () => {
  it('returns the supplied message for a blank value', () => {
    expect(validateRequired('   ', FIRST_NAME_REQUIRED_MESSAGE)).toBe('نام الزامی است');
  });

  it('returns null for a filled value', () => {
    expect(validateRequired('سارا', FIRST_NAME_REQUIRED_MESSAGE)).toBeNull();
  });
});
