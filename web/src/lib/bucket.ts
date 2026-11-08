const NO_DATA_BUCKET = 0;
const BUCKET_COUNT = 5;

/**
 * 1 (lowest) to 5 (highest) for a count, placed within the range of the counts shown for this scenario.
 * A suppressed year is bucket 0. When every count is equal the middle bucket is used.
 */
export function bucketInRange(count: number | null, counts: (number | null)[]): number {
  if (count === null) {
    return NO_DATA_BUCKET;
  }
  const shown = counts.filter((value): value is number => value !== null);
  const low = Math.min(...shown);
  const high = Math.max(...shown);
  if (high === low) {
    return Math.ceil(BUCKET_COUNT / 2);
  }
  const share = (count - low) / (high - low);
  return Math.min(BUCKET_COUNT, 1 + Math.floor(share * BUCKET_COUNT));
}
