export interface ChartPoint {
  year: number;
  count: number | null;
}

export interface Band {
  center: number;
  swingPct: number;
}

interface Frame {
  width: number;
  height: number;
  padLeft: number;
  padRight: number;
  padTop: number;
  padBottom: number;
}

interface Plotted {
  year: number;
  count: number;
  x: number;
  y: number;
}

export interface ChartLayout {
  points: Plotted[];
  /** Line segments, one per run of years with a count. A suppressed year breaks the line. */
  paths: string[];
  band: { top: number; height: number } | null;
}

/** Turn yearly counts and a noise band into SVG coordinates. Counts and years only, no drawing. */
export function layoutChart(points: ChartPoint[], band: Band | null, frame: Frame): ChartLayout {
  const shown = points.filter((point): point is { year: number; count: number } => point.count !== null);
  if (shown.length === 0) {
    return { points: [], paths: [], band: null };
  }
  const counts = shown.map((point) => point.count);
  const bandLow = band ? band.center * (1 - band.swingPct / 100) : Infinity;
  const bandHigh = band ? band.center * (1 + band.swingPct / 100) : -Infinity;
  const low = Math.min(...counts, bandLow);
  const high = Math.max(...counts, bandHigh);
  const span = high - low || 1;
  const years = points.map((point) => point.year);
  const firstYear = Math.min(...years);
  const yearSpan = Math.max(...years) - firstYear || 1;
  const innerWidth = frame.width - frame.padLeft - frame.padRight;
  const innerHeight = frame.height - frame.padTop - frame.padBottom;
  const toX = (year: number) => frame.padLeft + ((year - firstYear) / yearSpan) * innerWidth;
  const toY = (count: number) => frame.padTop + (1 - (count - low) / span) * innerHeight;

  const plotted = shown.map((point) => ({ ...point, x: toX(point.year), y: toY(point.count) }));
  const paths: string[] = [];
  let run: Plotted[] = [];
  for (const point of points) {
    const found = plotted.find((item) => item.year === point.year);
    if (found) {
      run.push(found);
    } else if (run.length > 0) {
      paths.push(toPath(run));
      run = [];
    }
  }
  if (run.length > 0) {
    paths.push(toPath(run));
  }
  return {
    points: plotted,
    paths,
    band: band ? { top: toY(bandHigh), height: toY(bandLow) - toY(bandHigh) } : null,
  };
}

function toPath(run: Plotted[]): string {
  return run.map((point, index) => `${index === 0 ? "M" : "L"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
}
