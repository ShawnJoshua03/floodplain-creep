import { bucketOf, computeBreaks } from "./exposureBreaks";

describe("exposureBreaks", () => {
  it("splits counts into five groups of about equal size", () => {
    const breaks = computeBreaks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100]);
    expect(breaks).toEqual([30, 50, 70, 90]);
    const buckets = [10, 30, 50, 70, 100].map((count) => bucketOf(count, breaks));
    expect(buckets).toEqual([1, 2, 3, 4, 5]);
  });

  it("gives a suppressed neighborhood its own bucket", () => {
    expect(bucketOf(null, [1, 2, 3, 4])).toBe(0);
  });

  it("returns no thresholds for no data", () => {
    expect(computeBreaks([])).toEqual([]);
  });
});
