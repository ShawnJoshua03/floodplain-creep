import { baseStyle, contextLayers, OUTLINE_LAYER, overlayLayer, WATER_LAYER } from "./mapStyle";
import type { Palette } from "./readPalette";

const palette: Palette = { background: "bg", accent: "accent", water: "water" };

describe("mapStyle", () => {
  it("has no basemap sources", () => {
    expect(baseStyle(palette).sources).toEqual({});
  });

  it("draws water under the outline, and the outline in the accent color", () => {
    const layers = contextLayers(palette);
    expect(layers.map((layer) => layer.id)).toEqual([WATER_LAYER, OUTLINE_LAYER]);
    expect(layers[0]?.paint).toMatchObject({ "fill-color": "water" });
    expect(layers[1]?.paint).toMatchObject({ "line-color": "accent" });
  });

  it("softens the depth image with linear resampling", () => {
    expect(overlayLayer().paint).toMatchObject({ "raster-resampling": "linear" });
  });
});
