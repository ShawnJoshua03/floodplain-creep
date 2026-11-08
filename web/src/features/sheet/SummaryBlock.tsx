import styles from "./SummaryBlock.module.css";

interface SummaryBlockProps {
  label: string;
  value: string;
  note: string;
}

export function SummaryBlock({ label, value, note }: SummaryBlockProps) {
  return (
    <div className={styles.block}>
      <p className={styles.label}>{label}</p>
      <p className={styles.value}>{value}</p>
      <p className={styles.note}>{note}</p>
    </div>
  );
}
