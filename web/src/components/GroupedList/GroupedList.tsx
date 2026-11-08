import type { ReactNode } from "react";
import { ChevronIcon } from "../icons/icons";
import styles from "./GroupedList.module.css";

interface GroupedListProps {
  title?: string;
  footer?: string;
  children: ReactNode;
}

export function GroupedList({ title, footer, children }: GroupedListProps) {
  return (
    <section className={styles.section}>
      {title ? <h2 className={styles.title}>{title}</h2> : null}
      <ul className={styles.list}>{children}</ul>
      {footer ? <p className={styles.footer}>{footer}</p> : null}
    </section>
  );
}

interface RowProps {
  label: string;
  value?: string;
  onPress?: () => void;
}

export function Row({ label, value, onPress }: RowProps) {
  const content = (
    <>
      <span className={styles.label}>{label}</span>
      {value ? <span className={styles.value}>{value}</span> : null}
      {onPress ? <ChevronIcon className={styles.chevron} /> : null}
    </>
  );
  return (
    <li>
      {onPress ? (
        <button type="button" className={styles.row} onClick={onPress}>
          {content}
        </button>
      ) : (
        <div className={styles.row}>{content}</div>
      )}
    </li>
  );
}
