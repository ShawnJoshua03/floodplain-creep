import tokensCss from "./tokens.css?raw";

const TEXT_MIN = 4.5;
const GRAPHIC_MIN = 3;
const STEP_MIN = 1.2;
const NODATA_MIN = 1.3;
const DEPTH_FLOOR = 1.8;

type Rgba = { r: number; g: number; b: number; a: number };

function readTokens(css: string): Map<string, string> {
  const tokens = new Map<string, string>();
  for (const match of css.matchAll(/(--[\w-]+):\s*(#[0-9a-fA-F]{6,8})\s*;/g)) {
    const [, name, value] = match;
    if (name && value) {
      tokens.set(name, value);
    }
  }
  return tokens;
}

function parseHex(hex: string): Rgba {
  const channel = (start: number) => parseInt(hex.slice(start, start + 2), 16);
  return { r: channel(1), g: channel(3), b: channel(5), a: hex.length === 9 ? channel(7) / 255 : 1 };
}

function over(top: Rgba, below: Rgba): Rgba {
  const mix = (a: number, b: number) => a * top.a + b * (1 - top.a);
  return { r: mix(top.r, below.r), g: mix(top.g, below.g), b: mix(top.b, below.b), a: 1 };
}

function luminance({ r, g, b }: Rgba): number {
  const linear = (value: number) => {
    const c = value / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b);
}

function ratio(first: Rgba, second: Rgba): number {
  const [light, dark] = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return ((light ?? 0) + 0.05) / ((dark ?? 0) + 0.05);
}

const [baseCss = "", moreContrastCss = ""] = tokensCss.split("@media (prefers-contrast: more)");
const baseTokens = readTokens(baseCss);
const moreContrastTokens = new Map([...baseTokens, ...readTokens(moreContrastCss)]);

function color(tokens: Map<string, string>, name: string): Rgba {
  const value = tokens.get(name);
  if (!value) {
    throw new Error(`Token ${name} is missing or not a hex color`);
  }
  const parsed = parseHex(value);
  return parsed.a < 1 ? over(parsed, color(tokens, "--bg-grouped")) : parsed;
}

const TEXT_PAIRS: [string, string][] = [
  ["--label", "--bg"],
  ["--label", "--bg-grouped"],
  ["--label", "--bg-row"],
  ["--label", "--chrome-bg"],
  ["--label", "--fill-control-selected"],
  ["--label-secondary", "--bg-row"],
  ["--label-secondary", "--chrome-bg"],
  ["--label-secondary", "--fill-control"],
  ["--label-tertiary", "--bg-row"],
  ["--accent", "--bg"],
  ["--accent", "--bg-row"],
  ["--accent", "--chrome-bg"],
  ["--accent-contrast", "--accent"],
];

const GRAPHIC_PAIRS: [string, string][] = [
  ["--label-tertiary", "--bg-row"],
  ["--control-edge", "--bg-row"],
  ["--control-edge", "--chrome-bg"],
  ["--control-edge", "--bg-grouped"],
  ["--accent", "--bg-row"],
  ["--label", "--accent"],
  ["--label", "--fill-control"],
  ["--label-tertiary", "--bg-grouped"],
];

describe.each([
  ["default", baseTokens],
  ["increased contrast", moreContrastTokens],
])("contrast in %s", (_name, tokens) => {
  it.each(TEXT_PAIRS)("text %s on %s is at least 4.5 to 1", (foreground, background) => {
    expect(ratio(color(tokens, foreground), color(tokens, background))).toBeGreaterThanOrEqual(TEXT_MIN);
  });

  it.each(GRAPHIC_PAIRS)("icon or control edge %s on %s is at least 3 to 1", (foreground, background) => {
    expect(ratio(color(tokens, foreground), color(tokens, background))).toBeGreaterThanOrEqual(GRAPHIC_MIN);
  });
});

describe("data ramps", () => {
  const exposure = [1, 2, 3, 4, 5].map((n) => `--ramp-exposure-${n}`);
  const depth = [1, 2, 3, 4].map((n) => `--ramp-depth-${n}`);

  it.each([
    ["exposure", exposure],
    ["depth", depth],
  ])("the %s ramp gets brighter at every step and stays distinguishable", (_name, steps) => {
    for (let index = 1; index < steps.length; index += 1) {
      const lower = color(baseTokens, steps[index - 1] ?? "");
      const higher = color(baseTokens, steps[index] ?? "");
      expect(luminance(higher)).toBeGreaterThan(luminance(lower));
      expect(ratio(higher, lower)).toBeGreaterThanOrEqual(STEP_MIN);
    }
  });

  it("the no-data fill is distinguishable from every exposure step", () => {
    for (const step of exposure) {
      expect(ratio(color(baseTokens, step), color(baseTokens, "--fill-nodata"))).toBeGreaterThanOrEqual(NODATA_MIN);
    }
  });

  it("the dimmest depth step still shows against the map background", () => {
    expect(ratio(color(baseTokens, "--ramp-depth-1"), color(baseTokens, "--bg-grouped"))).toBeGreaterThanOrEqual(
      DEPTH_FLOOR,
    );
  });
});
