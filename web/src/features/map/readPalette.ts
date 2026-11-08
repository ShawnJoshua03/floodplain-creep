export interface Palette {
  background: string;
  separator: string;
  accent: string;
  noData: string;
  exposure: string[];
  fadeMs: number;
}

const EXPOSURE_TOKENS = [1, 2, 3, 4, 5].map((step) => `--ramp-exposure-${step}`);

/** Map colors are read from the CSS tokens at runtime, so no color is written twice. */
export function readPalette(root: HTMLElement = document.documentElement): Palette {
  const style = getComputedStyle(root);
  const read = (name: string) => style.getPropertyValue(name).trim();
  return {
    background: read("--bg-grouped"),
    separator: read("--separator"),
    accent: read("--accent"),
    noData: read("--fill-nodata"),
    exposure: EXPOSURE_TOKENS.map(read),
    fadeMs: Number.parseFloat(read("--map-fade")) || 0,
  };
}
