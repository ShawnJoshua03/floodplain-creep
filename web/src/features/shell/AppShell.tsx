import { useEffect, useMemo, useState } from "react";
import { useFocus, useGrowth, useOverlay, useWater } from "../../api/hooks";
import { Scrubber } from "../../components/Scrubber/Scrubber";
import { formatCount } from "../../lib/format";
import { useSelection } from "../../state/SelectionProvider";
import { MapLegend } from "../map/MapLegend";
import { MapView } from "../map/MapView";
import { LimitsDialog } from "../sheet/LimitsDialog";
import { SheetPanel } from "../sheet/SheetPanel";
import { InfoButton } from "./InfoButton";
import { usePlayback } from "./usePlayback";

const MAP_LABEL =
  "Map of the neighborhood outline with modeled flood depth and permanent water. The panel has the numbers.";

export function AppShell() {
  const { year, returnPeriod, overlayOn, focusName, setYear } = useSelection();
  const focus = useFocus(returnPeriod);
  const overlay = useOverlay(returnPeriod, overlayOn);
  const water = useWater();
  const growth = useGrowth(returnPeriod);
  const [limitsOpen, setLimitsOpen] = useState(false);
  const firstYear = focus.data?.first_year ?? year;
  const lastYear = focus.data?.last_year ?? year;
  const playback = usePlayback(year, firstYear, lastYear, setYear);

  const current = focus.data?.series.find((row) => row.year === year)?.buildings_in_zone ?? null;
  const overlayImage = useMemo(
    () => (overlayOn && overlay.data ? { url: overlay.data.image_url, bounds: overlay.data.bounds } : null),
    [overlayOn, overlay.data],
  );
  const mapTag = current === null ? `${focusName}, ${year}` : `${focusName}, ${year}: ${formatCount(current)} buildings`;
  const growthUrls = growth.data?.image_urls;
  useEffect(() => {
    for (const url of Object.values(growthUrls ?? {})) {
      new Image().src = url;
    }
  }, [growthUrls]);
  const growthImage = useMemo(() => {
    const url = growth.data?.image_urls[String(year)];
    return growth.data && url ? { url, bounds: growth.data.bounds } : null;
  }, [growth.data, year]);
  const announcement =
    current === null
      ? ""
      : `${focusName}, ${year}, ${returnPeriod}-year flood, ${formatCount(current)} buildings in the modeled flood zone`;

  return (
    <>
      <MapView
        label={MAP_LABEL}
        tag={mapTag}
        geometry={focus.data?.neighborhood.geometry ?? null}
        water={water.data?.geometry ?? null}
        overlay={overlayImage}
        growth={growthImage}
      />
      <MapLegend
        depthBins={overlayOn && overlay.data ? overlay.data.bins : null}
        growth={growth.data ? { bins: growth.data.bins, blockMeters: growth.data.block_m } : null}
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
