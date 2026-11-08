import styles from "./InlineMessage.module.css";

interface InlineMessageProps {
  kind: "loading" | "error" | "empty" | "info";
  children: string;
  onRetry?: () => void;
}

export function InlineMessage({ kind, children, onRetry }: InlineMessageProps) {
  const role = kind === "error" ? "alert" : "status";
  const classes = kind === "empty" ? `${styles.message} ${styles.centered}` : styles.message;
  return (
    <div className={classes} role={role}>
      {kind === "loading" ? <progress className={styles.progress} aria-label={children} /> : null}
      <p>{children}</p>
      {kind === "error" && onRetry ? (
        <button type="button" className={styles.retry} onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}
