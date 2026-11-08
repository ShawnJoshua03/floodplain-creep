import type { ReactNode } from "react";
import styles from "./Sheet.module.css";

interface SheetProps {
  label: string;
  children: ReactNode;
}

export function Sheet({ label, children }: SheetProps) {
  return (
    <aside className={`${styles.sheet} chrome`} aria-label={label}>
      <div className={styles.body}>{children}</div>
    </aside>
  );
}
