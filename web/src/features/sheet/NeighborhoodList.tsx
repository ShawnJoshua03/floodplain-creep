import { useState } from "react";
import { useNeighborhoods } from "../../api/hooks";
import { GroupedList, Row } from "../../components/GroupedList/GroupedList";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { formatCount, NOT_ENOUGH_DATA } from "../../lib/format";
import { rankNeighborhoods } from "../../lib/neighborhoodList";
import { useSelection } from "../../state/SelectionProvider";

const TOP_COUNT = 6;

export function NeighborhoodList() {
  const { returnPeriod, year, selectNeighborhood } = useSelection();
  const query = useNeighborhoods(returnPeriod, year);
  const [showAll, setShowAll] = useState(false);

  if (query.isPending) {
    return <InlineMessage kind="loading">Loading neighborhoods</InlineMessage>;
  }
  if (query.isError) {
    return (
      <InlineMessage kind="error" onRetry={() => void query.refetch()}>
        The neighborhoods did not load.
      </InlineMessage>
    );
  }
  const ranked = rankNeighborhoods(query.data.features.map((feature) => feature.properties));
  if (ranked.length === 0) {
    return <InlineMessage kind="empty">No neighborhoods to show.</InlineMessage>;
  }
  const visible = showAll ? ranked : ranked.slice(0, TOP_COUNT);
  return (
    <GroupedList title="Neighborhoods" footer="Buildings in the modeled flood zone, highest first.">
      {visible.map((item) => (
        <Row
          key={item.neighborhood_id}
          label={item.name}
          value={item.buildings_in_zone === null ? NOT_ENOUGH_DATA : formatCount(item.buildings_in_zone)}
          onPress={() => selectNeighborhood(item.neighborhood_id)}
        />
      ))}
      {ranked.length > TOP_COUNT ? (
        <Row label={showAll ? "Show fewer" : "Show all"} onPress={() => setShowAll(!showAll)} />
      ) : null}
    </GroupedList>
  );
}
