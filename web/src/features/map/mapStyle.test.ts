import { baseStyle, fillColor, neighborhoodLayers, selectedFilter, SELECTED_LAYER, SUPPRESSED_LAYER } from "./mapStyle";
import type { Palette } from "./readPalette";

const palette: Palette = {
  background: "bg",
  separator: "sep",
  accent: "accent",
  noData: "nodata",
  exposure: ["e1", "e2", "e3", "e4", "e5"],
  fadeMs: 400,
};

describe("mapStyle", () => {
  it("has no basemap sources", () => {
    expect(baseStyle(palette).sources).toEqual({});
  });

  it("maps each bucket to its ramp color and falls back to the no-data fill", () => {
    expect(fillColor(palette)).toEqual([
      "match",
      ["coalesce", ["feature-state", "bucket"], 0],
      1, "e1", 2, "e2", 3, "e3", 4, "e4", 5, "e5",
      "nodata",
    ]);
  });

  it("draws a dashed outline only for suppressed neighborhoods and a selection outline", () => {
    const layers = neighborhoodLayers(palette);
    const suppressed = layers.find((layer) => layer.id === SUPPRESSED_LAYER);
    expect(suppressed?.paint).toMatchObject({ "line-dasharray": [2, 2] });
    expect(JSON.stringify(suppressed?.paint)).toContain("feature-state");
    expect(layers.some((layer) => layer.id === SELECTED_LAYER)).toBe(true);
  });

  it("matches no neighborhood when nothing is selected", () => {
    expect(selectedFilter(null)).toEqual(["==", ["get", "neighborhood_id"], ""]);
    expect(selectedFilter("n1")).toEqual(["==", ["get", "neighborhood_id"], "n1"]);
  });
});
