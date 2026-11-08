import type { LayerSpecification, StyleSpecification } from "maplibre-gl";
import type { Palette } from "./readPalette";

export const FOCUS_SOURCE = "focus";
export const WATER_SOURCE = "water";
export const OVERLAY_SOURCE = "depth-overlay";
export const GROWTH_SOURCE = "growth-overlay";
export const GROWTH_LAYER = "growth-overlay-layer";
export const WATER_LAYER = "water-fill";
export const OVERLAY_LAYER = "depth-overlay-layer";
export const OUTLINE_LAYER = "focus-outline";

const OVERLAY_OPACITY = 0.85;
const GROWTH_OPACITY = 0.9;
const OUTLINE_WIDTH = 2.5;

/** No basemap tiles. The background is a flat color, and water and flood depth are drawn from our own data. */
export function baseStyle(palette: Palette): StyleSpecification {
  return {
    version: 8,
    sources: {},
    layers: [{ id: "background", type: "background", paint: { "background-color": palette.background } }],
  };
}

/** Bottom to top: permanent water, then the neighborhood outline. The depth image goes between them. */
export function contextLayers(palette: Palette): LayerSpecification[] {
  return [
    { id: WATER_LAYER, type: "fill", source: WATER_SOURCE, paint: { "fill-color": palette.water } },
    {
      id: OUTLINE_LAYER,
      type: "line",
      source: FOCUS_SOURCE,
      paint: { "line-color": palette.accent, "line-width": OUTLINE_WIDTH },
    },
  ];
}

/** Linear resampling softens the 100 m squares. The image is a model, and it is labeled as one. */
export function overlayLayer(): LayerSpecification {
  return {
    id: OVERLAY_LAYER,
    type: "raster",
    source: OVERLAY_SOURCE,
    paint: { "raster-opacity": OVERLAY_OPACITY, "raster-fade-duration": 0, "raster-resampling": "linear" },
  };
}

/** Building density in the flood zone, one image per year. Drawn above the depth image. */
export function growthLayer(): LayerSpecification {
  return {
    id: GROWTH_LAYER,
    type: "raster",
    source: GROWTH_SOURCE,
    paint: { "raster-opacity": GROWTH_OPACITY, "raster-fade-duration": 0, "raster-resampling": "linear" },
  };
}
