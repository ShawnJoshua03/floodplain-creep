import type { LayerSpecification, StyleSpecification } from "maplibre-gl";
import type { Palette } from "./readPalette";

export const SOURCE_ID = "focus";
export const FILL_LAYER = "focus-fill";
export const OUTLINE_LAYER = "focus-outline";
export const OVERLAY_SOURCE = "depth-overlay";
export const OVERLAY_LAYER = "depth-overlay-layer";

const OVERLAY_OPACITY = 0.7;
const OUTLINE_WIDTH = 2;
const FILL_OPACITY = 0.85;
/** The fill steps back while depth is shown, so blue over amber does not turn muddy. */
const FILL_OPACITY_UNDER_OVERLAY = 0.3;

/** No basemap tiles. The background is a flat color. */
export function baseStyle(palette: Palette): StyleSpecification {
  return {
    version: 8,
    sources: {},
    layers: [{ id: "background", type: "background", paint: { "background-color": palette.background } }],
  };
}

/** Bucket 1 to 5 reads the exposure ramp. Bucket 0 is a suppressed year. */
export function fillColor(palette: Palette, bucket: number): string {
  return palette.exposure[bucket - 1] ?? palette.noData;
}

export function fillOpacity(overlayOn: boolean): number {
  return overlayOn ? FILL_OPACITY_UNDER_OVERLAY : FILL_OPACITY;
}

export function focusLayers(palette: Palette, bucket: number, overlayOn: boolean): LayerSpecification[] {
  return [
    {
      id: FILL_LAYER,
      type: "fill",
      source: SOURCE_ID,
      paint: {
        "fill-color": fillColor(palette, bucket),
        "fill-color-transition": { duration: palette.fadeMs, delay: 0 },
        "fill-opacity": fillOpacity(overlayOn),
        "fill-opacity-transition": { duration: palette.fadeMs, delay: 0 },
      },
    },
    {
      id: OUTLINE_LAYER,
      type: "line",
      source: SOURCE_ID,
      paint: { "line-color": palette.accent, "line-width": OUTLINE_WIDTH },
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
