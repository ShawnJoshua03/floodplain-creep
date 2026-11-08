import styles from "./Takeaway.module.css";

/** The claim, in one sentence, before any chart or table. */
export function Takeaway({ children }: { children: string }) {
  return <p className={styles.takeaway}>{children}</p>;
}
