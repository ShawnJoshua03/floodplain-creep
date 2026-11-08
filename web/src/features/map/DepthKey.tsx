import type { CSSProperties } from "react";
import { binLabel, binPosition, PERSON_HEIGHT_M, SCALE_TOP_M } from "../../lib/depthKey";
import styles from "./DepthKey.module.css";

interface Bin {
  min_depth_m: number;
  max_depth_m: number | null;
  color: string;
}

/** Four depth bins drawn beside a person of known height. */
export function DepthKey({ bins }: { bins: Bin[] }) {
  return (
    <div className={styles.key}>
      <h2 className={styles.heading}>Modeled flood depth</h2>
      <div className={styles.scale}>
        <div className={styles.person} style={{ "--person-share": String(PERSON_HEIGHT_M / SCALE_TOP_M) } as CSSProperties}>
          <svg viewBox="0 0 24 64" className={styles.figure} aria-hidden="true" focusable="false">
            <circle cx="12" cy="6" r="5" />
            <path d="M5 16h14a3 3 0 0 1 3 3v19h-4v24h-6V44h-2v18H6V38H2V19a3 3 0 0 1 3-3z" />
          </svg>
          <span className={styles.personLabel}>{PERSON_HEIGHT_M} m</span>
        </div>
        <ul className={styles.bins}>
          {bins.map((bin) => {
            const { from, to } = binPosition(bin);
            return (
              <li
                key={bin.min_depth_m}
                className={styles.bin}
                style={{ "--from": String(from), "--to": String(to), "--bin-color": bin.color } as CSSProperties}
              >
                <span className={styles.swatch} />
                <span>{binLabel(bin)}</span>
              </li>
            );
          })}
        </ul>
      </div>
      <p className={styles.note}>Modeled and approximate. A simulated scenario, not a forecast.</p>
    </div>
  );
}
