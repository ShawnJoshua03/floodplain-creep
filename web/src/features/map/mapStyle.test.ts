import { baseStyle, fillColor, fillOpacity, focusLayers, OUTLINE_LAYER } from "./mapStyle";
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

  it("reads the exposure ramp by bucket and uses the no-data fill for bucket 0", () => {
    expect(fillColor(palette, 1)).toBe("e1");
    expect(fillColor(palette, 5)).toBe("e5");
    expect(fillColor(palette, 0)).toBe("nodata");
  });

  it("dims the fill while the depth overlay is on", () => {
    expect(fillOpacity(true)).toBeLessThan(fillOpacity(false));
  });

  it("outlines the neighborhood in the accent color", () => {
    const outline = focusLayers(palette, 3, false).find((layer) => layer.id === OUTLINE_LAYER);
    expect(outline?.paint).toMatchObject({ "line-color": "accent" });
  });
});
