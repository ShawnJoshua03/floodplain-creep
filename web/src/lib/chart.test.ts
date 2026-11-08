import { layoutChart } from "./chart";

const frame = { width: 200, height: 100, padLeft: 0, padRight: 0, padTop: 0, padBottom: 0 };

describe("layoutChart", () => {
  it("puts the first year at the left edge and the last at the right edge", () => {
    const layout = layoutChart(
      [
        { year: 2018, count: 100 },
        { year: 2023, count: 200 },
      ],
      null,
      frame,
    );
    expect(layout.points.map((point) => point.x)).toEqual([0, 200]);
  });

  it("draws a higher count nearer the top", () => {
    const layout = layoutChart(
      [
        { year: 2018, count: 100 },
        { year: 2019, count: 200 },
      ],
      null,
      frame,
    );
    const [first, second] = layout.points;
    expect(second?.y).toBeLessThan(first?.y ?? 0);
  });

  it("breaks the line at a suppressed year", () => {
    const layout = layoutChart(
      [
        { year: 2018, count: 100 },
        { year: 2019, count: null },
        { year: 2020, count: 120 },
        { year: 2021, count: 130 },
      ],
      null,
      frame,
    );
    expect(layout.paths).toHaveLength(2);
  });

  it("sizes the noise band as a share of its center and keeps it inside the frame", () => {
    const layout = layoutChart(
      [
        { year: 2018, count: 100 },
        { year: 2023, count: 150 },
      ],
      { center: 100, swingPct: 10 },
      frame,
    );
    expect(layout.band).not.toBeNull();
    expect(layout.band?.top ?? -1).toBeGreaterThanOrEqual(0);
    expect((layout.band?.top ?? 0) + (layout.band?.height ?? 0)).toBeLessThanOrEqual(frame.height);
  });

  it("returns nothing to draw when every year is suppressed", () => {
    expect(layoutChart([{ year: 2018, count: null }], null, frame)).toEqual({ points: [], paths: [], band: null });
  });
});
