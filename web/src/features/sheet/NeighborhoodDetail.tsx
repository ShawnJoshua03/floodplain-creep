import { useBrief, useCitySummary, useNeighborhoods } from "../../api/hooks";
import type { Brief, NeighborhoodProperties } from "../../api/types";
import { GroupedList, Row } from "../../components/GroupedList/GroupedList";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { formatCount, formatGrowth, formatSigned, NOT_AVAILABLE } from "../../lib/format";
import { useSelection } from "../../state/SelectionProvider";
import styles from "./NeighborhoodDetail.module.css";

const BRIEF_FOOTNOTE: Record<Brief["source"], string> = {
  gemini: "Written from the numbers above. Numbers checked.",
  template: "Written from a fixed template and the numbers above.",
};

function BriefSection({ neighborhoodId, returnPeriod }: { neighborhoodId: string; returnPeriod: number }) {
  const query = useBrief(neighborhoodId, returnPeriod);
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
      <p className={styles.footnote}>{BRIEF_FOOTNOTE[query.data.source]}</p>
    </section>
  );
}

function Counts({ item, firstYear }: { item: NeighborhoodProperties; firstYear: number }) {
  const stock = item.buildings_in_zone === null ? NOT_AVAILABLE : formatCount(item.buildings_in_zone);
  const change = item.new_buildings_in_zone === null ? NOT_AVAILABLE : formatSigned(item.new_buildings_in_zone);
  const growth = item.growth_pct === null ? NOT_AVAILABLE : formatGrowth(item.growth_pct);
  return (
    <GroupedList title={`${item.year}, ${item.return_period}-year flood`}>
      <Row label="Buildings in the modeled flood zone" value={stock} />
      <Row label={`New since ${firstYear}`} value={change} />
      <Row label={`Growth since ${firstYear}`} value={growth} />
    </GroupedList>
  );
}

export function NeighborhoodDetail({ neighborhoodId }: { neighborhoodId: string }) {
  const { returnPeriod, year } = useSelection();
  const neighborhoods = useNeighborhoods(returnPeriod, year);
  const summary = useCitySummary(returnPeriod);

  if (neighborhoods.isPending || summary.isPending) {
    return <InlineMessage kind="loading">Loading neighborhood</InlineMessage>;
  }
  if (neighborhoods.isError || summary.isError) {
    return (
      <InlineMessage
        kind="error"
        onRetry={() => {
          void neighborhoods.refetch();
          void summary.refetch();
        }}
      >
        The neighborhood did not load.
      </InlineMessage>
    );
  }
  const item = neighborhoods.data.features.find((feature) => feature.properties.neighborhood_id === neighborhoodId)
    ?.properties;
  if (!item) {
    return <InlineMessage kind="empty">This neighborhood has no data for the selected year.</InlineMessage>;
  }
  return (
    <div className={styles.detail}>
      {item.suppressed ? (
        <InlineMessage kind="info">
          {`Fewer than ${summary.data.min_count_k} buildings are in the modeled flood zone here this year, so no number is shown.`}
        </InlineMessage>
      ) : null}
      <Counts item={item} firstYear={summary.data.first_year} />
      <BriefSection neighborhoodId={neighborhoodId} returnPeriod={returnPeriod} />
    </div>
  );
}
