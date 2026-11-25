import { describe, expect, it } from 'vitest';
import {
  buildMonthCells,
  dateKey,
  formatEventTime,
  formatJalaliDate,
  gregorianToJalali,
  isJalaliLeapYear,
  jalaliDateKey,
  jalaliMonthLength,
  jalaliToGregorian,
  monthLabel,
  toPersianDigits,
} from '../calendar';

describe('calendar helpers (F-033)', () => {
  it('converts digits to Persian', () => {
    expect(toPersianDigits(2026)).toBe('۲۰۲۶');
    expect(toPersianDigits('2026-12-01')).toBe('۲۰۲۶-۱۲-۰۱');
  });

  it('converts between Gregorian and Jalali dates', () => {
    expect(gregorianToJalali(2026, 11, 25)).toEqual({ jy: 1405, jm: 9, jd: 4 });
    expect(gregorianToJalali(2026, 1, 1)).toEqual({ jy: 1404, jm: 10, jd: 11 });
    expect(jalaliToGregorian(1405, 1, 1)).toEqual({ gy: 2026, gm: 3, gd: 21 });
  });

  it('knows Esfand length in leap and common years', () => {
    expect(isJalaliLeapYear(1403)).toBe(true);
    expect(jalaliMonthLength(1403, 12)).toBe(30);
    expect(isJalaliLeapYear(1405)).toBe(false);
    expect(jalaliMonthLength(1405, 12)).toBe(29);
    expect(jalaliMonthLength(1405, 1)).toBe(31);
    expect(jalaliMonthLength(1405, 7)).toBe(30);
  });

  it('labels a Jalali month in Persian', () => {
    expect(monthLabel(1405, 9)).toBe('آذر ۱۴۰۵');
    expect(monthLabel(1405, 1)).toBe('فروردین ۱۴۰۵');
  });

  it('starts Azar 1405 on Sunday (the second column of a Saturday-first week)', () => {
    const cells = buildMonthCells(1405, 9);

    // 1405-09-01 is 2026-11-22, a Sunday: Saturday, then Sunday.
    expect(cells.slice(0, 2)).toEqual([null, 1]);
    expect(cells).toHaveLength(35);
    expect(cells.filter((day) => day !== null)).toHaveLength(30);
  });

  it('round-trips every month boundary of 1405', () => {
    for (let jm = 1; jm <= 12; jm += 1) {
      for (const jd of [1, jalaliMonthLength(1405, jm)]) {
        const g = jalaliToGregorian(1405, jm, jd);
        expect(gregorianToJalali(g.gy, g.gm, g.gd)).toEqual({ jy: 1405, jm, jd });
      }
    }
  });

  it('builds ISO day keys and Jalali labels from stored keys', () => {
    expect(dateKey(2026, 1, 5)).toBe('2026-01-05');
    expect(dateKey(2026, 12, 31)).toBe('2026-12-31');
    expect(jalaliDateKey(1405, 9, 4)).toBe('2026-11-25');
    expect(formatJalaliDate('2026-11-25')).toBe('۴ آذر ۱۴۰۵');
  });

  it('labels an event time in Persian digits and tolerates a missing time', () => {
    expect(formatEventTime('14:30:00')).toBe('۱۴:۳۰');
    expect(formatEventTime('08:05')).toBe('۰۸:۰۵');
    expect(formatEventTime(null)).toBe('');
  });
});
