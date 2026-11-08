/** Time between years while the time-lapse plays. The time-lapse never starts on its own. */
export const PLAY_STEP_MS = 1200;

/** The next year in a time-lapse, or null when the last year is reached. */
export function nextYear(current: number, last: number): number | null {
  return current < last ? current + 1 : null;
}
