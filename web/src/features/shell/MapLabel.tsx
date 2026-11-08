import styles from "./MapLabel.module.css";

/** The neighborhood name on hover or selection. The map itself carries no text. */
export function MapLabel({ name }: { name: string | undefined }) {
  if (!name) {
    return null;
  }
  return (
    <p className={`${styles.label} chrome`} aria-hidden="true">
      {name}
    </p>
  );
}
