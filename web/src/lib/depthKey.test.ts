import { binLabel, binPosition, PERSON_HEIGHT_M, SCALE_TOP_M } from "./depthKey";

describe("depthKey", () => {
  it("places a bin as shares of the scale height", () => {
    const { from, to } = binPosition({ min_depth_m: 0.5, max_depth_m: 1 });
    expect(from).toBeCloseTo(0.5 / SCALE_TOP_M);
    expect(to).toBeCloseTo(1 / SCALE_TOP_M);
  });

  it("draws the deepest bin up to the top of the scale", () => {
    expect(binPosition({ min_depth_m: 2, max_depth_m: null }).to).toBe(1);
  });

  it("keeps a person inside the scale", () => {
    expect(PERSON_HEIGHT_M).toBeLessThan(SCALE_TOP_M);
  });

  it("words each bin in metres", () => {
    expect(binLabel({ min_depth_m: 0.1, max_depth_m: 0.5 })).toBe("0.1 to 0.5 m");
    expect(binLabel({ min_depth_m: 2, max_depth_m: null })).toBe("2 m and deeper");
  });
});
