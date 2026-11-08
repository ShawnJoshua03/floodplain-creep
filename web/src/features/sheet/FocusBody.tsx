import { useFocus } from "../../api/hooks";
import type { FocusView } from "../../api/types";
import { GroupedList, Row } from "../../components/GroupedList/GroupedList";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { formatCount, formatGrowth, formatSigned, NOT_AVAILABLE } from "../../lib/format";
import { balanceSentence, otherNeighborhoodsNote, ratioText, takeawaySentence } from "../../lib/verdict";
import { useSelection } from "../../state/SelectionProvider";
import { EvidenceChart } from "./EvidenceChart";
import { SummaryBlock } from "./SummaryBlock";
import { Takeaway } from "./Takeaway";

function swingText(noise: FocusView["noise"]): string {
  return noise ? `±${noise.typical_swing_pct.toFixed(1)}%` : NOT_AVAILABLE;
}

function timesText(signal: FocusView["signal"]): string {
  return signal.times_typical_swing === null ? NOT_AVAILABLE : `${signal.times_typical_swing.toFixed(1)} times`;
}

function coverageNote(view: FocusView): string {
  const share = Math.round(view.neighborhood.coverage * 100);
  return `Counts cover ${share}% of ${view.neighborhood.name}, the part inside the study area.`;
}

function Headline({ view, year }: { view: FocusView; year: number }) {
  const row = view.series.find((item) => item.year === year);
  if (!row || row.buildings_in_zone === null) {
    return (
      <InlineMessage kind="info">
        {`Fewer than ${view.min_count_k} buildings are in the modeled flood zone in ${year}, so no number is shown.`}
      </InlineMessage>
    );
  }
  const change =
    row.new_buildings_in_zone === null
      ? `No change figure for ${year}.`
      : `${formatSigned(row.new_buildings_in_zone)} since ${view.first_year}.`;
  return (
    <SummaryBlock
      label={`Buildings in the modeled ${view.return_period}-year flood zone, ${year}`}
      value={formatCount(row.buildings_in_zone)}
      note={`${change} ${coverageNote(view)}`}
    />
  );
}

function Evidence({ view }: { view: FocusView }) {
  const { signal, balance, noise, neighborhood } = view;
  const focusRatio = balance ? ratioText(balance.focus.cells_gaining, balance.focus.cells_losing) : null;
  const restRatio = balance ? ratioText(balance.rest_of_city.cells_gaining, balance.rest_of_city.cells_losing) : null;
  const footer = [balanceSentence(neighborhood.name, balance), otherNeighborhoodsNote(neighborhood.name)]
    .filter(Boolean)
    .join(" ");
  return (
    <GroupedList title="Is the growth real?" footer={footer}>
      <Row
        label="Change, averaged over two years at each end"
        value={signal.smoothed_change_pct === null ? NOT_AVAILABLE : formatGrowth(signal.smoothed_change_pct)}
      />
      <Row label="Usual yearly swing in the rest of Dhaka" value={swingText(noise)} />
      <Row label="Change compared with the swing" value={timesText(signal)} />
      <Row label={`Areas gaining for each losing, ${neighborhood.name}`} value={focusRatio ?? NOT_AVAILABLE} />
      <Row label="Areas gaining for each losing, rest of Dhaka" value={restRatio ?? NOT_AVAILABLE} />
    </GroupedList>
  );
}

export function FocusBody() {
  const { returnPeriod, year } = useSelection();
  const query = useFocus(returnPeriod);

  if (query.isPending) {
    return <InlineMessage kind="loading">Loading the evidence</InlineMessage>;
  }
  if (query.isError) {
    return (
      <InlineMessage kind="error" onRetry={() => void query.refetch()}>
        The data did not load.
      </InlineMessage>
    );
  }
  const view = query.data;
  const points = view.series.map((row) => ({ year: row.year, count: row.buildings_in_zone }));
  const first = view.series[0]?.buildings_in_zone ?? null;
  const band = view.noise && first !== null ? { center: first, swingPct: view.noise.typical_swing_pct } : null;
  return (
    <>
      <Takeaway>{takeawaySentence(view)}</Takeaway>
      <Headline view={view} year={year} />
      <EvidenceChart
        points={points}
        band={band}
        selectedYear={year}
        caption={
          band
            ? `The shaded band is the usual yearly swing in the rest of Dhaka, ${swingText(view.noise)}, drawn around ${view.first_year}. Move the year to see the line grow.`
            : "Not enough data to draw the usual yearly swing."
        }
      />
      <Evidence view={view} />
    </>
  );
}
