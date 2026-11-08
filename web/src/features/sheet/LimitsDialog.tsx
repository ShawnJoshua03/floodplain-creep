import { useLimits } from "../../api/hooks";
import { Dialog } from "../../components/Dialog/Dialog";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import styles from "./LimitsDialog.module.css";

interface LimitsDialogProps {
  open: boolean;
  onClose: () => void;
}

export function LimitsDialog({ open, onClose }: LimitsDialogProps) {
  const query = useLimits(open);
  return (
    <Dialog open={open} title="Limits and misuse notice" onClose={onClose}>
      {query.isPending ? <InlineMessage kind="loading">Loading limits</InlineMessage> : null}
      {query.isError ? (
        <InlineMessage kind="error" onRetry={() => void query.refetch()}>
          The limits did not load.
        </InlineMessage>
      ) : null}
      {query.data ? (
        <>
          <ul className={styles.list}>
            {query.data.limits.map((limit) => (
              <li key={limit}>{limit}</li>
            ))}
          </ul>
          <p className={styles.notice}>{query.data.misuse_notice}</p>
        </>
      ) : null}
    </Dialog>
  );
}
