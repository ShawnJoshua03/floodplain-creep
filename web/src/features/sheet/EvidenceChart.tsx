import { type Band, type ChartPoint, layoutChart } from "../../lib/chart";
import { formatCount } from "../../lib/format";
import styles from "./EvidenceChart.module.css";

interface EvidenceChartProps {
  points: ChartPoint[];
  band: Band | null;
  selectedYear: number;
  caption: string;
}

const FRAME = { width: 320, height: 200, padLeft: 54, padRight: 14, padTop: 14, padBottom: 30 };
const DOT_RADIUS = 3;
const SELECTED_RADIUS = 6;
const LABEL_OFFSET = 10;
const AXIS_GAP = 8;

function describe(points: ChartPoint[]): string {
  const parts = points.map(
    (point) => `${point.year} ${point.count === null ? "not enough data" : formatCount(point.count)}`,
  );
  return `Buildings in the modeled flood zone by year: ${parts.join(", ")}. The shaded band is the usual yearly swing.`;
}

function dotClass(year: number, selectedYear: number): string {
  if (year === selectedYear) {
    return `${styles.dot ?? ""} ${styles.selected ?? ""}`;
  }
  return (year < selectedYear ? styles.dot : styles.dotAhead) ?? "";
}

/** Yearly counts as a line that is drawn up to the selected year, with the usual yearly swing as a labeled band. */
export function EvidenceChart({ points, band, selectedYear, caption }: EvidenceChartProps) {
  const layout = layoutChart(points, band, FRAME, selectedYear);
  const first = layout.points[0];
  const last = layout.points[layout.points.length - 1];
  const right = FRAME.width - FRAME.padRight;
  return (
    <figure className={styles.figure}>
      <figcaption className={styles.heading}>Buildings in the modeled flood zone</figcaption>
      <svg viewBox={`0 0 ${FRAME.width} ${FRAME.height}`} className={styles.chart} role="img" aria-label={describe(points)}>
        {layout.ticks.map((tick) => (
          <g key={tick.value}>
            <line className={styles.grid} x1={FRAME.padLeft} x2={right} y1={tick.y} y2={tick.y} />
            <text className={styles.axis} x={FRAME.padLeft - AXIS_GAP} y={tick.y} textAnchor="end" dominantBaseline="middle">
              {formatCount(Math.round(tick.value))}
            </text>
          </g>
        ))}
        {layout.band ? (
          <>
            <rect className={styles.band} x={FRAME.padLeft} width={right - FRAME.padLeft} y={layout.band.top} height={layout.band.height} />
            <text className={styles.bandLabel} x={right - AXIS_GAP / 2} y={layout.band.top - AXIS_GAP / 2} textAnchor="end">
              usual yearly swing
            </text>
          </>
        ) : null}
        {layout.ghostPaths.map((path) => (
          <path key={path} className={styles.ghost} d={path} />
        ))}
        {layout.paths.map((path) => (
          <path key={path} className={styles.line} d={path} />
        ))}
        {layout.points.map((point) => (
          <circle
            key={point.year}
            className={dotClass(point.year, selectedYear)}
            cx={point.x}
            cy={point.y}
            r={point.year === selectedYear ? SELECTED_RADIUS : DOT_RADIUS}
          />
        ))}
        {first ? (
          <text className={styles.axis} x={first.x} y={FRAME.height - LABEL_OFFSET} textAnchor="middle">
            {first.year}
          </text>
        ) : null}
        {last ? (
          <text className={styles.axis} x={last.x} y={FRAME.height - LABEL_OFFSET} textAnchor="middle">
            {last.year}
          </text>
        ) : null}
      </svg>
      <p className={styles.caption}>{caption}</p>
    </figure>
  );
}
