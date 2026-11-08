import type { CSSProperties } from "react";
import { formatCount } from "../../lib/format";
import styles from "./GrowthKey.module.css";

export interface GrowthBin {
  min_buildings: number;
  max_buildings: number | null;
  color: string;
}

function binLabel(bin: GrowthBin): string {
  return bin.max_buildings === null
    ? `${formatCount(bin.min_buildings)} or more`
    : `${formatCount(bin.min_buildings)} to ${formatCount(bin.max_buildings - 1)}`;
}

/** Buildings in the modeled flood zone per block, blended on the map. Blocks below the minimum count are hidden. */
export function GrowthKey({ bins, blockMeters }: { bins: GrowthBin[]; blockMeters: number }) {
  return (
    <div className={styles.key}>
      <h2 className={styles.heading}>Buildings in the flood zone</h2>
      <ul className={styles.bins}>
        {bins.map((bin) => (
          <li key={bin.min_buildings} className={styles.bin} style={{ "--bin-color": bin.color } as CSSProperties}>
            <span className={styles.swatch} />
            <span>{binLabel(bin)}</span>
          </li>
        ))}
      </ul>
      <p className={styles.note}>{`Per ${blockMeters} m block. Blocks with fewer buildings are hidden.`}</p>
    </div>
  );
}
