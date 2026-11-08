import { useValidation } from "../../api/hooks";
import type { ValidationResult } from "../../api/types";
import { GroupedList, Row } from "../../components/GroupedList/GroupedList";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { formatCount, formatInterval } from "../../lib/format";
import styles from "./AccuracyDetail.module.css";

function labelSourceNote(sources: ValidationResult["label_sources"]): string {
  return `${formatCount(sources.ai)} labels from an AI reviewer, ${formatCount(sources.audit)} checked by a person, ${formatCount(sources.human)} labeled by a person.`;
}

function Result({ result }: { result: ValidationResult }) {
  const unaudited = result.label_sources.ai > 0 && result.label_sources.audit === 0 && result.label_sources.human === 0;
  return (
    <div className={styles.detail}>
      {unaudited ? (
        <InlineMessage kind="info">These labels come from an AI reviewer. A person has not checked them yet.</InlineMessage>
      ) : null}
      <GroupedList
        title="Does a flagged increase match the imagery?"
        footer={`Tuned on ${formatCount(result.tuning_cells)} cells and measured on ${formatCount(result.test_cells)} other cells. Ranges are 95 percent intervals.`}
      >
        <Row label="Accuracy" value={formatInterval(result.accuracy)} />
        <Row label="Precision" value={formatInterval(result.precision)} />
        <Row label="Recall" value={formatInterval(result.recall)} />
        <Row label="Labeled cells" value={formatCount(result.labeled_cells)} />
        <Row label="Unclear cells left out" value={formatCount(result.excluded_unclear)} />
      </GroupedList>
      <section className={styles.method}>
        <h2 className={styles.heading}>Sampling method</h2>
        <p className={styles.text}>{result.sampling_note}</p>
        <p className={styles.text}>{labelSourceNote(result.label_sources)}</p>
        <p className={styles.text}>{`Imagery: ${result.imagery_source}. ${result.imagery_dates}.`}</p>
      </section>
    </div>
  );
}

export function AccuracyDetail() {
  const query = useValidation();
  if (query.isPending) {
    return <InlineMessage kind="loading">Loading accuracy</InlineMessage>;
  }
  if (query.isError) {
    return (
      <InlineMessage kind="error" onRetry={() => void query.refetch()}>
        The accuracy result did not load.
      </InlineMessage>
    );
  }
  return <Result result={query.data} />;
}
