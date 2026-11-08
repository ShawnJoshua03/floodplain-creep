import { type KeyboardEvent, useId, useRef } from "react";
import styles from "./SegmentedControl.module.css";

interface SegmentOption<T extends string | number> {
  value: T;
  label: string;
}

interface SegmentedControlProps<T extends string | number> {
  label: string;
  options: SegmentOption<T>[];
  value: T;
  onChange: (value: T) => void;
}

const STEP_KEYS: Record<string, number> = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };

export function SegmentedControl<T extends string | number>({
  label,
  options,
  value,
  onChange,
}: SegmentedControlProps<T>) {
  const name = useId();
  const inputs = useRef<(HTMLInputElement | null)[]>([]);

  function move(event: KeyboardEvent<HTMLInputElement>, index: number) {
    const step = STEP_KEYS[event.key];
    if (step === undefined) {
      return;
    }
    event.preventDefault();
    const next = (index + step + options.length) % options.length;
    const option = options[next];
    if (option) {
      onChange(option.value);
      inputs.current[next]?.focus();
    }
  }

  return (
    <fieldset className={styles.group}>
      <legend className="visually-hidden">{label}</legend>
      {options.map((option, index) => (
        <label key={option.value} className={styles.option}>
          <input
            ref={(node) => {
              inputs.current[index] = node;
            }}
            className={styles.input}
            type="radio"
            name={name}
            checked={option.value === value}
            onChange={() => onChange(option.value)}
            onKeyDown={(event) => move(event, index)}
          />
          <span className={styles.face}>{option.label}</span>
        </label>
      ))}
    </fieldset>
  );
}
