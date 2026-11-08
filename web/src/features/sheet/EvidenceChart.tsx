import { type Band, type ChartPoint, layoutChart } from "../../lib/chart";
import { formatCount } from "../../lib/format";
import styles from "./EvidenceChart.module.css";

interface EvidenceChartProps {
  points: ChartPoint[];
  band: Band | null;
  selectedYear: number;
  caption: string;
}

const FRAME = { width: 320, height: 150, padLeft: 12, padRight: 12, padTop: 12, padBottom: 24 };
const DOT_RADIUS = 3;
const SELECTED_RADIUS = 5.5;
const LABEL_OFFSET = 8;

function describe(points: ChartPoint[]): string {
  const parts = points.map((point) => `${point.year} ${point.count === null ? "not enough data" : formatCount(point.count)}`);
  return `Buildings in the modeled flood zone by year: ${parts.join(", ")}. The shaded band is the typical year-to-year swing.`;
}

/** Yearly counts as a line, with the typical swing as a band around the first year. */
export function EvidenceChart({ points, band, selectedYear, caption }: EvidenceChartProps) {
  const layout = layoutChart(points, band, FRAME);
  const first = layout.points[0];
  const last = layout.points[layout.points.length - 1];
  return (
    <figure className={styles.figure}>
      <figcaption className={styles.heading}>Buildings in the modeled flood zone</figcaption>
      <svg viewBox={`0 0 ${FRAME.width} ${FRAME.height}`} className={styles.chart} role="img" aria-label={describe(points)}>
        {layout.band ? (
          <rect
            className={styles.band}
            x={FRAME.padLeft}
            width={FRAME.width - FRAME.padLeft - FRAME.padRight}
            y={layout.band.top}
            height={layout.band.height}
          />
        ) : null}
        {layout.paths.map((path) => (
          <path key={path} className={styles.line} d={path} />
        ))}
        {layout.points.map((point) => (
          <circle
            key={point.year}
            className={point.year === selectedYear ? `${styles.dot} ${styles.selected}` : styles.dot}
            cx={point.x}
            cy={point.y}
            r={point.year === selectedYear ? SELECTED_RADIUS : DOT_RADIUS}
          />
        ))}
        {first ? (
          <text className={styles.axis} x={first.x} y={FRAME.height - LABEL_OFFSET} textAnchor="start">
            {first.year}
          </text>
        ) : null}
        {last ? (
          <text className={styles.axis} x={last.x} y={FRAME.height - LABEL_OFFSET} textAnchor="end">
            {last.year}
          </text>
        ) : null}
      </svg>
      <p className={styles.caption}>{caption}</p>
    </figure>
  );
}
