import { useCitySummary } from "../../api/hooks";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { SegmentedControl } from "../../components/SegmentedControl/SegmentedControl";
import { formatCount, formatSigned, NOT_AVAILABLE } from "../../lib/format";
import { useSelection } from "../../state/SelectionProvider";
import { SummaryBlock } from "./SummaryBlock";

export function CityTotals() {
  const { returnPeriod, year, setReturnPeriod } = useSelection();
  const query = useCitySummary(returnPeriod);

  if (query.isPending) {
    return <InlineMessage kind="loading">Loading city totals</InlineMessage>;
  }
  if (query.isError) {
    return (
      <InlineMessage kind="error" onRetry={() => void query.refetch()}>
        The city totals did not load.
      </InlineMessage>
    );
  }
  const summary = query.data;
  const current = summary.years.find((item) => item.year === year);
  const options = summary.return_periods.map((value) => ({ value, label: `${value}-year` }));
  return (
    <>
      <SegmentedControl label="Flood scenario" options={options} value={returnPeriod} onChange={setReturnPeriod} />
      {current ? (
        <SummaryBlock
          label={`New buildings in the modeled flood zone since ${summary.first_year}`}
          value={current.new_buildings_in_zone === null ? NOT_AVAILABLE : formatSigned(current.new_buildings_in_zone)}
          note={`${formatCount(current.neighborhoods_shown)} neighborhoods counted. ${formatCount(current.neighborhoods_suppressed)} with not enough data are left out.`}
        />
      ) : (
        <InlineMessage kind="empty">No totals for this year.</InlineMessage>
      )}
    </>
  );
}
