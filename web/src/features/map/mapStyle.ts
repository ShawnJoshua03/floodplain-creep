import type { ExpressionSpecification, LayerSpecification, StyleSpecification } from "maplibre-gl";
import type { Palette } from "./readPalette";

export const SOURCE_ID = "neighborhoods";
export const FILL_LAYER = "neighborhood-fill";
export const SEPARATOR_LAYER = "neighborhood-separator";
export const SUPPRESSED_LAYER = "neighborhood-suppressed";
export const SELECTED_LAYER = "neighborhood-selected";
export const OVERLAY_SOURCE = "depth-overlay";
export const OVERLAY_LAYER = "depth-overlay-layer";
export const ID_PROPERTY = "neighborhood_id";

const OVERLAY_OPACITY = 0.7;
export const FILL_OPACITY = 1;
/** The choropleth steps back while depth is shown, so blue over amber does not turn muddy. */
export const FILL_OPACITY_UNDER_OVERLAY = 0.35;
const SEPARATOR_WIDTH = 1;
const SELECTED_WIDTH = 2;
const SUPPRESSED_DASH = [2, 2];

/** No basemap tiles. The background is a flat color. */
export function baseStyle(palette: Palette): StyleSpecification {
  return {
    version: 8,
    sources: {},
    layers: [{ id: "background", type: "background", paint: { "background-color": palette.background } }],
  };
}

export function fillColor(palette: Palette): ExpressionSpecification {
  const steps = palette.exposure.flatMap((color, index) => [index + 1, color]);
  const expression = ["match", ["coalesce", ["feature-state", "bucket"], 0], ...steps, palette.noData];
  return expression as ExpressionSpecification;
}

export function neighborhoodLayers(palette: Palette): LayerSpecification[] {
  return [
    {
      id: FILL_LAYER,
      type: "fill",
      source: SOURCE_ID,
      paint: {
        "fill-color": fillColor(palette),
        "fill-color-transition": { duration: palette.fadeMs, delay: 0 },
        "fill-opacity": FILL_OPACITY,
        "fill-opacity-transition": { duration: palette.fadeMs, delay: 0 },
      },
    },
    {
      id: SEPARATOR_LAYER,
      type: "line",
      source: SOURCE_ID,
      paint: { "line-color": palette.separator, "line-width": SEPARATOR_WIDTH },
    },
    {
      id: SUPPRESSED_LAYER,
      type: "line",
      source: SOURCE_ID,
      paint: {
        "line-color": palette.separator,
        "line-width": SEPARATOR_WIDTH,
        "line-dasharray": SUPPRESSED_DASH,
        "line-opacity": ["case", ["==", ["coalesce", ["feature-state", "bucket"], 0], 0], 1, 0],
      },
    },
    {
      id: SELECTED_LAYER,
      type: "line",
      source: SOURCE_ID,
      filter: ["==", ["get", ID_PROPERTY], ""],
      paint: { "line-color": palette.accent, "line-width": SELECTED_WIDTH },
    },
  ];
}

export function overlayLayer(): LayerSpecification {
  return {
    id: OVERLAY_LAYER,
    type: "raster",
    source: OVERLAY_SOURCE,
    paint: { "raster-opacity": OVERLAY_OPACITY, "raster-fade-duration": 0 },
  };
}

export function selectedFilter(id: string | null): ExpressionSpecification {
  return ["==", ["get", ID_PROPERTY], id ?? ""];
}
