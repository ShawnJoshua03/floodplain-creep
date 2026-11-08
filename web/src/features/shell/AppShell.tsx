import { useMemo, useState } from "react";
import { useCitySummary, useNeighborhoods, useOverlay } from "../../api/hooks";
import { Scrubber } from "../../components/Scrubber/Scrubber";
import { bucketOf, computeBreaks } from "../../lib/exposureBreaks";
import { formatCount } from "../../lib/format";
import { useSelection } from "../../state/SelectionProvider";
import { type MapGeometry, MapView } from "../map/MapView";
import { LimitsDialog } from "../sheet/LimitsDialog";
import { SheetPanel } from "../sheet/SheetPanel";
import { InfoButton } from "./InfoButton";
import { MapLabel } from "./MapLabel";
import { usePlayback } from "./usePlayback";

const MAP_LABEL =
  "Map of neighborhoods shaded by buildings in the modeled flood zone. The list in the panel has the same numbers.";

export function AppShell() {
  const { year, returnPeriod, neighborhoodId, overlayOn, setYear, selectNeighborhood } = useSelection();
  const summary = useCitySummary(returnPeriod);
  const lastYear = summary.data?.last_year ?? year;
  const firstYear = summary.data?.first_year ?? year;
  const current = useNeighborhoods(returnPeriod, year);
  const reference = useNeighborhoods(returnPeriod, lastYear);
  const overlay = useOverlay(returnPeriod, overlayOn);
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [limitsOpen, setLimitsOpen] = useState(false);
  const playback = usePlayback(year, lastYear, setYear);

  const geometries = useMemo<MapGeometry[]>(
    () =>
      (reference.data?.features ?? []).map((feature) => ({
        id: feature.properties.neighborhood_id,
        geometry: feature.geometry,
      })),
    [reference.data],
  );
  const buckets = useMemo(() => {
    const shown = (reference.data?.features ?? []).flatMap((feature) => feature.properties.buildings_in_zone ?? []);
    const breaks = computeBreaks(shown);
    return Object.fromEntries(
      (current.data?.features ?? []).map((feature) => [
        feature.properties.neighborhood_id,
        bucketOf(feature.properties.buildings_in_zone, breaks),
      ]),
    );
  }, [reference.data, current.data]);

  const overlayImage = useMemo(
    () => (overlayOn && overlay.data ? { url: overlay.data.image_url, bounds: overlay.data.bounds } : null),
    [overlayOn, overlay.data],
  );
  const names = new Map((current.data?.features ?? []).map((f) => [f.properties.neighborhood_id, f.properties.name]));
  const totals = summary.data?.years.find((item) => item.year === year);
  const announcement = totals
    ? `${year}, ${returnPeriod}-year flood, ${formatCount(totals.buildings_in_zone)} buildings in the modeled flood zone`
    : "";

  return (
    <>
      <MapView
        label={MAP_LABEL}
        geometries={geometries}
        buckets={buckets}
        selectedId={neighborhoodId}
        overlay={overlayImage}
        onSelect={selectNeighborhood}
        onHover={setHoverId}
      />
      <MapLabel name={names.get(hoverId ?? neighborhoodId ?? "")} />
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
