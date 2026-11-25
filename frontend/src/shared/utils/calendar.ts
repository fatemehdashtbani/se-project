/**
 * Date helpers for the calendar page (F-033).
 *
 * The grid follows the Jalali (Persian) calendar and starts on Saturday. Month
 * names, digits and conversions are computed here so the page does not depend
 * on the runtime's ICU data and every browser shows the same dates.
 *
 * The API stores dates as ISO Gregorian day keys (`YYYY-MM-DD`); conversion
 * happens at the page boundary via `jalaliDateKey` and `formatJalaliDate`.
 * The conversion algorithm is the well-known arithmetic one used by
 * jalaali-js (MIT), inlined here to avoid a new runtime dependency.
 */

export const JALALI_MONTHS = [
  'فروردین',
  'اردیبهشت',
  'خرداد',
  'تیر',
  'مرداد',
  'شهریور',
  'مهر',
  'آبان',
  'آذر',
  'دی',
  'بهمن',
  'اسفند',
] as const;

/** Columns of the month grid, Saturday first. */
export const PERSIAN_WEEKDAYS = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'] as const;

const PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹';

const JALALI_BREAKS = [
  -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394,
  2456, 3178,
];

export interface JalaliDate {
  jy: number;
  jm: number;
  jd: number;
}

export interface GregorianDate {
  gy: number;
  gm: number;
  gd: number;
}

function div(a: number, b: number): number {
  return Math.trunc(a / b);
}

function mod(a: number, b: number): number {
  return a - Math.trunc(a / b) * b;
}

interface JalaliYearInfo {
  leap: number;
  gy: number;
  march: number;
}

function jalCal(jy: number): JalaliYearInfo {
  const bl = JALALI_BREAKS.length;
  const gy = jy + 621;
  let leapJ = -14;
  let jp = JALALI_BREAKS[0];
  let jump = 0;

  if (jy < jp || jy >= JALALI_BREAKS[bl - 1]) {
    throw new Error(`Invalid Jalali year ${jy}`);
  }

  for (let i = 1; i < bl; i += 1) {
    const jm = JALALI_BREAKS[i];
    jump = jm - jp;
    if (jy < jm) {
      break;
    }
    leapJ = leapJ + div(jump, 33) * 8 + div(mod(jump, 33), 4);
    jp = jm;
  }

  let n = jy - jp;

  leapJ = leapJ + div(n, 33) * 8 + div(mod(n, 33) + 3, 4);
  if (mod(jump, 33) === 4 && jump - n === 4) {
    leapJ += 1;
  }

  const leapG = div(gy, 4) - div((div(gy, 100) + 1) * 3, 4) - 150;
  const march = 20 + leapJ - leapG;

  if (jump - n < 6) {
    n = n - jump + div(jump + 4, 33) * 33;
  }
  let leap = mod(mod(n + 1, 33) - 1, 4);
  if (leap === -1) {
    leap = 4;
  }

  return { leap, gy, march };
}

/** Julian day number for a Gregorian date (`gm` is 1-based). */
function gregorianToDayNumber(gy: number, gm: number, gd: number): number {
  let day =
    div((gy + div(gm - 8, 6) + 100100) * 1461, 4) +
    div(153 * mod(gm + 9, 12) + 2, 5) +
    gd -
    34840408;

  day = day - div(div(gy + 100100 + div(gm - 8, 6), 100) * 3, 4) + 752;
  return day;
}

function dayNumberToGregorian(dayNumber: number): GregorianDate {
  let j = 4 * dayNumber + 139361631;
  j = j + div(div(4 * dayNumber + 183187720, 146097) * 3, 4) * 4 - 3908;

  const i = div(mod(j, 1461), 4) * 5 + 308;
  const gd = div(mod(i, 153), 5) + 1;
  const gm = mod(div(i, 153), 12) + 1;
  const gy = div(j, 1461) - 100100 + div(8 - gm, 6);

  return { gy, gm, gd };
}

function jalaliToDayNumber(jy: number, jm: number, jd: number): number {
  const info = jalCal(jy);
  return (
    gregorianToDayNumber(info.gy, 3, info.march) + (jm - 1) * 31 - div(jm, 7) * (jm - 7) + jd - 1
  );
}

function dayNumberToJalali(dayNumber: number): JalaliDate {
  const { gy } = dayNumberToGregorian(dayNumber);
  let jy = gy - 621;
  const info = jalCal(jy);
  const firstFarvardin = gregorianToDayNumber(gy, 3, info.march);

  let k = dayNumber - firstFarvardin;
  if (k >= 0) {
    if (k <= 185) {
      return { jy, jm: 1 + div(k, 31), jd: mod(k, 31) + 1 };
    }
    k -= 186;
  } else {
    jy -= 1;
    k += 179;
    if (info.leap === 1) {
      k += 1;
    }
  }

  return { jy, jm: 7 + div(k, 30), jd: mod(k, 30) + 1 };
}

/** Convert a Gregorian date (`gm` is 1-based) to its Jalali equivalent. */
export function gregorianToJalali(gy: number, gm: number, gd: number): JalaliDate {
  return dayNumberToJalali(gregorianToDayNumber(gy, gm, gd));
}

/** Convert a Jalali date (`jm` is 1-based) to its Gregorian equivalent. */
export function jalaliToGregorian(jy: number, jm: number, jd: number): GregorianDate {
  return dayNumberToGregorian(jalaliToDayNumber(jy, jm, jd));
}

export function isJalaliLeapYear(jy: number): boolean {
  return jalCal(jy).leap === 0;
}

/** Days in a Jalali month; Esfand has 29 days, or 30 in a leap year. */
export function jalaliMonthLength(jy: number, jm: number): number {
  if (jm <= 6) {
    return 31;
  }
  if (jm <= 11) {
    return 30;
  }
  return isJalaliLeapYear(jy) ? 30 : 29;
}

export function toPersianDigits(value: number | string): string {
  return String(value).replace(/\d/g, (digit) => PERSIAN_DIGITS[Number(digit)]);
}

/** e.g. «آذر ۱۴۰۵» for month 9 of 1405. */
export function monthLabel(jy: number, jm: number): string {
  return `${JALALI_MONTHS[jm - 1]} ${toPersianDigits(jy)}`;
}

/**
 * Day numbers of a Jalali month (`jm` is 1-based) padded with `null` so the
 * first day lands under its weekday column and every row has seven cells.
 */
export function buildMonthCells(jy: number, jm: number): (number | null)[] {
  const { gy, gm, gd } = jalaliToGregorian(jy, jm, 1);
  const firstWeekday = new Date(Date.UTC(gy, gm - 1, gd)).getUTCDay();
  const leadingBlanks = (firstWeekday + 1) % 7;
  const daysInMonth = jalaliMonthLength(jy, jm);

  const cells: (number | null)[] = Array<number | null>(leadingBlanks).fill(null);
  for (let day = 1; day <= daysInMonth; day += 1) {
    cells.push(day);
  }
  while (cells.length % 7 !== 0) {
    cells.push(null);
  }

  return cells;
}

/** ISO day key (`YYYY-MM-DD`) from a 1-based month, as the API stores it. */
export function dateKey(gy: number, gm: number, gd: number): string {
  const paddedMonth = String(gm).padStart(2, '0');
  const paddedDay = String(gd).padStart(2, '0');
  return `${gy}-${paddedMonth}-${paddedDay}`;
}

/** ISO Gregorian day key for a day of a Jalali month. */
export function jalaliDateKey(jy: number, jm: number, jd: number): string {
  const { gy, gm, gd } = jalaliToGregorian(jy, jm, jd);
  return dateKey(gy, gm, gd);
}

/** Jalali date of an ISO Gregorian day key. */
export function jalaliFromKey(key: string): JalaliDate {
  const [gy, gm, gd] = key.split('-').map(Number);
  return gregorianToJalali(gy, gm, gd);
}

/** e.g. «۴ آذر ۱۴۰۵» for the stored key `2026-11-25`. */
export function formatJalaliDate(key: string): string {
  const { jy, jm, jd } = jalaliFromKey(key);
  return `${toPersianDigits(jd)} ${JALALI_MONTHS[jm - 1]} ${toPersianDigits(jy)}`;
}

/** e.g. «۱۴:۳۰» for the stored time `14:30:00`; empty when no time is set. */
export function formatEventTime(value: string | null): string {
  if (!value) {
    return '';
  }

  const [hours = '00', minutes = '00'] = value.split(':');
  return toPersianDigits(`${hours.padStart(2, '0')}:${minutes.slice(0, 2).padStart(2, '0')}`);
}

/** The local calendar day as an ISO Gregorian day key. */
export function todayKey(): string {
  const now = new Date();
  return dateKey(now.getFullYear(), now.getMonth() + 1, now.getDate());
}

/** The local calendar day in the Jalali calendar. */
export function todayJalali(): JalaliDate {
  const now = new Date();
  return gregorianToJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
}
