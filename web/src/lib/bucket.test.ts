import { bucketInRange } from "./bucket";

describe("bucketInRange", () => {
  const counts = [100, 120, 140, 160, 180, 200];

  it("places the lowest count in bucket 1 and the highest in bucket 5", () => {
    expect(bucketInRange(100, counts)).toBe(1);
    expect(bucketInRange(200, counts)).toBe(5);
  });

  it("steps up through the range", () => {
    expect([100, 130, 150, 170, 190].map((count) => bucketInRange(count, counts))).toEqual([1, 2, 3, 4, 5]);
  });

  it("gives a suppressed year its own bucket", () => {
    expect(bucketInRange(null, counts)).toBe(0);
  });

  it("ignores suppressed years when finding the range", () => {
    expect(bucketInRange(200, [null, 100, 200])).toBe(5);
  });

  it("uses the middle bucket when every count is equal", () => {
    expect(bucketInRange(50, [50, 50])).toBe(3);
  });
});
