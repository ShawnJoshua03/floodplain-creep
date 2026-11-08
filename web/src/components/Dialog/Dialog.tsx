import { type ReactNode, useEffect, useRef } from "react";
import styles from "./Dialog.module.css";

interface DialogProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}

export function Dialog({ open, title, onClose, children }: DialogProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog || !open) {
      return undefined;
    }
    const opener = document.activeElement;
    dialog.showModal();
    return () => {
      dialog.close();
      if (opener instanceof HTMLElement) {
        opener.focus();
      }
    };
  }, [open]);

  return (
    <dialog
      ref={ref}
      className={`${styles.dialog} chrome`}
      aria-label={title}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <div className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
        <button type="button" className={styles.done} onClick={onClose}>
          Done
        </button>
      </div>
      {children}
    </dialog>
  );
}
