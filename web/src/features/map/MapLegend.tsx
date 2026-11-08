import { DepthKey } from "./DepthKey";
import styles from "./MapLegend.module.css";

interface Bin {
  min_depth_m: number;
  max_depth_m: number | null;
  color: string;
}

/** What the colors on the map mean, kept beside the map. Shown while flood depth is on. */
export function MapLegend({ bins }: { bins: Bin[] }) {
  return (
    <aside className={`${styles.legend} chrome`} aria-label="Map legend">
      <DepthKey bins={bins} />
      <p className={styles.water}>
        <span className={styles.waterSwatch} />
        <span>River or lake, water all year</span>
      </p>
    </aside>
  );
}
