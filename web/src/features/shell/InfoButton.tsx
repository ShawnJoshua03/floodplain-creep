import { InfoIcon } from "../../components/icons/icons";
import styles from "./InfoButton.module.css";

export function InfoButton({ onPress }: { onPress: () => void }) {
  return (
    <button type="button" className={`${styles.button} chrome`} onClick={onPress}>
      <InfoIcon />
      <span className="visually-hidden">Limits and misuse notice</span>
    </button>
  );
}
