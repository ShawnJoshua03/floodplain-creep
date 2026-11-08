import type { ReactNode } from "react";
import styles from "./Sheet.module.css";

interface SheetProps {
  label: string;
  expanded: boolean;
  onToggleExpanded: () => void;
  children: ReactNode;
}

export function Sheet({ label, expanded, onToggleExpanded, children }: SheetProps) {
  return (
    <aside className={`${styles.sheet} chrome`} aria-label={label} data-expanded={expanded}>
      <button type="button" className={styles.grabber} onClick={onToggleExpanded} aria-expanded={expanded}>
        <span className="visually-hidden">{expanded ? "Collapse panel" : "Expand panel"}</span>
      </button>
      <div className={styles.body}>{children}</div>
    </aside>
  );
}
