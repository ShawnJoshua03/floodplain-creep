import styles from "./SwitchRow.module.css";

interface SwitchRowProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function SwitchRow({ label, checked, onChange }: SwitchRowProps) {
  return (
    <label className={styles.row}>
      <span className={styles.label}>{label}</span>
      <input
        className={styles.input}
        type="checkbox"
        role="switch"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
    </label>
  );
}
