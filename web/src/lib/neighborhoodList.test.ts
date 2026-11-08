import { rankNeighborhoods } from "./neighborhoodList";

describe("rankNeighborhoods", () => {
  it("puts the highest count first and suppressed neighborhoods last", () => {
    const ranked = rankNeighborhoods([
      { name: "Zed", buildings_in_zone: null, suppressed: true },
      { name: "Low", buildings_in_zone: 40, suppressed: false },
      { name: "High", buildings_in_zone: 900, suppressed: false },
      { name: "Alpha", buildings_in_zone: null, suppressed: true },
    ]);
    expect(ranked.map((item) => item.name)).toEqual(["High", "Low", "Alpha", "Zed"]);
  });

  it("breaks ties by name", () => {
    const ranked = rankNeighborhoods([
      { name: "B", buildings_in_zone: 50, suppressed: false },
      { name: "A", buildings_in_zone: 50, suppressed: false },
    ]);
    expect(ranked.map((item) => item.name)).toEqual(["A", "B"]);
  });
});
