import { boundsOf } from "./geometryBounds";

describe("boundsOf", () => {
  it("finds the box around polygons and multipolygons", () => {
    const polygon = { coordinates: [[[0, 0], [2, 0], [2, 3], [0, 0]]] };
    const multi = { coordinates: [[[[5, -1], [6, -1], [6, 1], [5, -1]]]] };
    expect(boundsOf([polygon, multi])).toEqual([0, -1, 6, 3]);
  });

  it("returns null when there is nothing to measure", () => {
    expect(boundsOf([])).toBeNull();
  });
});
