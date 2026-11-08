import type { Ref } from "react";
import styles from "./LargeTitle.module.css";

interface LargeTitleProps {
  title: string;
  subtitle?: string;
  titleRef?: Ref<HTMLHeadingElement>;
}

export function LargeTitle({ title, subtitle, titleRef }: LargeTitleProps) {
  return (
    <div className={styles.block}>
      <h1 className={styles.title} tabIndex={-1} ref={titleRef}>
        {title}
      </h1>
      {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}
    </div>
  );
}
