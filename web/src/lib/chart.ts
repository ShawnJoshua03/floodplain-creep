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

interface Tick {
  value: number;
  y: number;
}

export interface ChartLayout {
  points: Plotted[];
  /** Line segments for years up to the selected year. A suppressed year breaks the line. */
  paths: string[];
  /** Line segments from the selected year onward, drawn faint so the climb is revealed as the year moves. */
  ghostPaths: string[];
  band: { top: number; height: number } | null;
  /** The lowest and highest values on the axis. */
  ticks: Tick[];
}

function toPath(run: Plotted[]): string {
  return run.map((point, index) => `${index === 0 ? "M" : "L"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
}

/** Runs of consecutive years that have a count and pass the test. Each run needs two points to draw. */
function runs(points: ChartPoint[], plotted: Plotted[], keep: (year: number) => boolean): string[] {
  const paths: string[] = [];
  let run: Plotted[] = [];
  const flush = () => {
    if (run.length > 1) {
      paths.push(toPath(run));
    }
    run = [];
  };
  for (const point of points) {
    const found = plotted.find((item) => item.year === point.year);
    if (found && keep(point.year)) {
      run.push(found);
    } else {
      flush();
    }
  }
  flush();
  return paths;
}

/** Turn yearly counts and a noise band into SVG coordinates. Counts and years only, no drawing. */
export function layoutChart(points: ChartPoint[], band: Band | null, frame: Frame, upToYear: number): ChartLayout {
  const shown = points.filter((point): point is { year: number; count: number } => point.count !== null);
  if (shown.length === 0) {
    return { points: [], paths: [], ghostPaths: [], band: null, ticks: [] };
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
  return {
    points: plotted,
    paths: runs(points, plotted, (year) => year <= upToYear),
    ghostPaths: runs(points, plotted, (year) => year >= upToYear),
    band: band ? { top: toY(bandHigh), height: toY(bandLow) - toY(bandHigh) } : null,
    ticks: [
      { value: high, y: toY(high) },
      { value: low, y: toY(low) },
    ],
  };
}
