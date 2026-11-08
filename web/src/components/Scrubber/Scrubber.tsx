import { PauseIcon, PlayIcon } from "../icons/icons";
import styles from "./Scrubber.module.css";

interface ScrubberProps {
  label: string;
  min: number;
  max: number;
  value: number;
  playing: boolean;
  onChange: (value: number) => void;
  onTogglePlay: () => void;
}

export function Scrubber({ label, min, max, value, playing, onChange, onTogglePlay }: ScrubberProps) {
  return (
    <div className={`${styles.scrubber} chrome`} role="group" aria-label={label}>
      <button type="button" className={styles.play} onClick={onTogglePlay}>
        {playing ? <PauseIcon /> : <PlayIcon />}
        <span className="visually-hidden">{playing ? "Pause" : "Play"}</span>
      </button>
      <input
        className={styles.range}
        type="range"
        aria-label="Year"
        min={min}
        max={max}
        step={1}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <output className={styles.year}>{value}</output>
    </div>
  );
}
