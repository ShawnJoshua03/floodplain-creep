const NO_DATA_BUCKET = 0;
const BUCKET_COUNT = 5;

/**
 * Thresholds that split shown counts into five equal-sized groups. They come from one reference
 * year, so a color means the same count in every year of the time-lapse.
 */
export function computeBreaks(counts: number[]): number[] {
  const sorted = [...counts].sort((a, b) => a - b);
  if (sorted.length === 0) {
    return [];
  }
  return Array.from({ length: BUCKET_COUNT - 1 }, (_, index) => {
    const position = Math.floor(((index + 1) * sorted.length) / BUCKET_COUNT);
    return sorted[Math.min(position, sorted.length - 1)] ?? 0;
  });
}

/** 1 (lowest) to 5 (highest) for a shown count, and 0 for a suppressed neighborhood. */
export function bucketOf(count: number | null, breaks: number[]): number {
  if (count === null) {
    return NO_DATA_BUCKET;
  }
  return 1 + breaks.filter((threshold) => count >= threshold).length;
}
