import { DepthKey } from "./DepthKey";
import { type GrowthBin, GrowthKey } from "./GrowthKey";
import styles from "./MapLegend.module.css";

interface DepthBin {
  min_depth_m: number;
  max_depth_m: number | null;
  color: string;
}

interface MapLegendProps {
  depthBins: DepthBin[] | null;
  growth: { bins: GrowthBin[]; blockMeters: number } | null;
}

/** What the colors on the map mean, kept beside the map. */
export function MapLegend({ depthBins, growth }: MapLegendProps) {
  return (
    <aside className={`${styles.legend} chrome`} aria-label="Map legend">
      {growth ? <GrowthKey bins={growth.bins} blockMeters={growth.blockMeters} /> : null}
      {depthBins ? <DepthKey bins={depthBins} /> : null}
      <p className={styles.water}>
        <span className={styles.waterSwatch} />
        <span>River or lake, water all year</span>
      </p>
    </aside>
  );
}
