import { formatCount, formatGrowth, formatInterval, formatShare, formatSigned } from "./format";

describe("format", () => {
  it("groups thousands", () => {
    expect(formatCount(6802)).toBe("6,802");
  });

  it("shows the sign of a change, including a true minus for a decrease", () => {
    expect(formatSigned(5434)).toBe("+5,434");
    expect(formatSigned(-496)).toBe("−496");
    expect(formatSigned(0)).toBe("0");
  });

  it("shows growth with one decimal and a sign", () => {
    expect(formatGrowth(16.2)).toBe("+16.2%");
    expect(formatGrowth(-6.8)).toBe("−6.8%");
  });

  it("shows a share as a whole percent", () => {
    expect(formatShare(0.5535)).toBe("55%");
  });

  it("shows a share with its range, or says it is not available", () => {
    expect(formatInterval({ value: 0.5535, low: 0.424, high: 0.676 })).toBe("55% (42% to 68%)");
    expect(formatInterval({ value: null, low: null, high: null })).toBe("Not available");
  });
});
