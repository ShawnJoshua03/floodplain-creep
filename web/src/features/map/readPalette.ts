export interface Palette {
  background: string;
  accent: string;
  water: string;
}

/** Map colors are read from the CSS tokens at runtime, so no color is written twice. */
export function readPalette(root: HTMLElement = document.documentElement): Palette {
  const style = getComputedStyle(root);
  const read = (name: string) => style.getPropertyValue(name).trim();
  return {
    background: read("--bg-grouped"),
    accent: read("--accent"),
    water: read("--map-water"),
  };
}
