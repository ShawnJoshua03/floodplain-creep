import { useBrief } from "../../api/hooks";
import type { Brief } from "../../api/types";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { useSelection } from "../../state/SelectionProvider";
import styles from "./BriefSection.module.css";

const FOOTNOTE: Record<Brief["source"], string> = {
  gemini: "Written from the numbers above. Numbers checked.",
  template: "Written from a fixed template and the numbers above.",
};

export function BriefSection() {
  const { returnPeriod } = useSelection();
  const query = useBrief(returnPeriod);
  if (query.isPending) {
    return <InlineMessage kind="loading">Loading summary</InlineMessage>;
  }
  if (query.isError) {
    return (
      <InlineMessage kind="error" onRetry={() => void query.refetch()}>
        The summary did not load.
      </InlineMessage>
    );
  }
  if (query.data === null) {
    return <InlineMessage kind="empty">No written summary yet.</InlineMessage>;
  }
  return (
    <section className={styles.summary}>
      <h2 className={styles.heading}>Summary</h2>
      <p className={styles.text}>{query.data.text}</p>
      <p className={styles.footnote}>{FOOTNOTE[query.data.source]}</p>
    </section>
  );
}
