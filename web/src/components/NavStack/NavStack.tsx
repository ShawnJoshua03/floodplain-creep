import { type ReactNode, useEffect, useRef } from "react";
import { ChevronIcon } from "../icons/icons";
import { LargeTitle } from "../LargeTitle/LargeTitle";
import styles from "./NavStack.module.css";

export interface NavView {
  key: string;
  title: string;
  subtitle?: string;
  content: ReactNode;
}

interface NavStackProps {
  views: NavView[];
  onBack: () => void;
}

export function NavStack({ views, onBack }: NavStackProps) {
  const top = views[views.length - 1];
  const previous = views[views.length - 2];
  const titleRef = useRef<HTMLHeadingElement>(null);
  const shownKey = useRef(top?.key);

  useEffect(() => {
    if (top && shownKey.current !== top.key) {
      shownKey.current = top.key;
      titleRef.current?.focus();
    }
  }, [top]);

  if (!top) {
    return null;
  }
  return (
    <div className={`${styles.stack} view-enter`} key={top.key}>
      {previous ? (
        <button type="button" className={styles.back} onClick={onBack}>
          <ChevronIcon className={styles.backIcon} />
          <span>{previous.title}</span>
        </button>
      ) : null}
      <LargeTitle title={top.title} subtitle={top.subtitle} titleRef={titleRef} />
      {top.content}
    </div>
  );
}
