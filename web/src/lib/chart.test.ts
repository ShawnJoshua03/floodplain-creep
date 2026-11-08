import { layoutChart } from "./chart";

const frame = { width: 200, height: 100, padLeft: 0, padRight: 0, padTop: 0, padBottom: 0 };
const two = [
  { year: 2018, count: 100 },
  { year: 2023, count: 200 },
];

describe("layoutChart", () => {
  it("puts the first year at the left edge and the last at the right edge", () => {
    expect(layoutChart(two, null, frame, 2023).points.map((point) => point.x)).toEqual([0, 200]);
  });

  it("draws a higher count nearer the top", () => {
    const [first, second] = layoutChart(two, null, frame, 2023).points;
    expect(second?.y).toBeLessThan(first?.y ?? 0);
  });

  it("breaks the line at a suppressed year", () => {
    const points = [
      { year: 2018, count: 100 },
      { year: 2019, count: 110 },
      { year: 2020, count: null },
      { year: 2021, count: 120 },
      { year: 2022, count: 130 },
    ];
    expect(layoutChart(points, null, frame, 2022).paths).toHaveLength(2);
  });

  it("draws the line up to the selected year and the rest faint", () => {
    const points = [2018, 2019, 2020, 2021].map((year, index) => ({ year, count: 100 + index * 10 }));
    const layout = layoutChart(points, null, frame, 2019);
    expect(layout.paths).toHaveLength(1);
    expect(layout.ghostPaths).toHaveLength(1);
    expect(layout.paths[0]).toContain("M0.0");
  });

  it("draws everything solid and nothing faint at the last year", () => {
    expect(layoutChart(two, null, frame, 2023).ghostPaths).toHaveLength(0);
  });

  it("marks the lowest and highest values on the axis", () => {
    const { ticks } = layoutChart(two, null, frame, 2023);
    expect(ticks.map((tick) => tick.value)).toEqual([200, 100]);
    expect(ticks[0]?.y).toBeLessThan(ticks[1]?.y ?? 0);
  });

  it("sizes the noise band as a share of its center and keeps it inside the frame", () => {
    const layout = layoutChart(two, { center: 100, swingPct: 10 }, frame, 2023);
    expect(layout.band?.top ?? -1).toBeGreaterThanOrEqual(0);
    expect((layout.band?.top ?? 0) + (layout.band?.height ?? 0)).toBeLessThanOrEqual(frame.height);
  });

  it("returns nothing to draw when every year is suppressed", () => {
    expect(layoutChart([{ year: 2018, count: null }], null, frame, 2018)).toEqual({
      points: [],
      paths: [],
      ghostPaths: [],
      band: null,
      ticks: [],
    });
  });
});
