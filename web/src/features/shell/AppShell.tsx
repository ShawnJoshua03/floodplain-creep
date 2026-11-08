import { useMemo, useState } from "react";
import { useFocus, useOverlay } from "../../api/hooks";
import { Scrubber } from "../../components/Scrubber/Scrubber";
import { bucketInRange } from "../../lib/bucket";
import { formatCount } from "../../lib/format";
import { useSelection } from "../../state/SelectionProvider";
import { MapView } from "../map/MapView";
import { LimitsDialog } from "../sheet/LimitsDialog";
import { SheetPanel } from "../sheet/SheetPanel";
import { InfoButton } from "./InfoButton";
import { usePlayback } from "./usePlayback";

const MAP_LABEL = "Map of the neighborhood outline with modeled flood depth. The panel has the numbers.";

export function AppShell() {
  const { year, returnPeriod, overlayOn, focusName, setYear } = useSelection();
  const focus = useFocus(returnPeriod);
  const overlay = useOverlay(returnPeriod, overlayOn);
  const [limitsOpen, setLimitsOpen] = useState(false);
  const firstYear = focus.data?.first_year ?? year;
  const lastYear = focus.data?.last_year ?? year;
  const playback = usePlayback(year, lastYear, setYear);

  const counts = useMemo(() => (focus.data?.series ?? []).map((row) => row.buildings_in_zone), [focus.data]);
  const current = focus.data?.series.find((row) => row.year === year)?.buildings_in_zone ?? null;
  const bucket = focus.data ? bucketInRange(current, counts) : 0;
  const overlayImage = useMemo(
    () => (overlayOn && overlay.data ? { url: overlay.data.image_url, bounds: overlay.data.bounds } : null),
    [overlayOn, overlay.data],
  );
  const announcement =
    current === null
      ? ""
      : `${focusName}, ${year}, ${returnPeriod}-year flood, ${formatCount(current)} buildings in the modeled flood zone`;

  return (
    <>
      <MapView
        label={MAP_LABEL}
        geometry={focus.data?.neighborhood.geometry ?? null}
        bucket={bucket}
        overlay={overlayImage}
      />
      <InfoButton onPress={() => setLimitsOpen(true)} />
      <SheetPanel onOpenLimits={() => setLimitsOpen(true)} />
      <Scrubber
        label="Year"
        min={firstYear}
        max={lastYear}
        value={year}
        playing={playback.playing}
        onChange={setYear}
        onTogglePlay={playback.toggle}
      />
      <div className="visually-hidden" aria-live="polite">
        {announcement}
      </div>
      <LimitsDialog open={limitsOpen} onClose={() => setLimitsOpen(false)} />
    </>
  );
}
