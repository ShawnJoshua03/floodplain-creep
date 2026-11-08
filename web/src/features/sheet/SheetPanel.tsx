import { useState } from "react";
import { useCitySummary, useNeighborhoods } from "../../api/hooks";
import { NavStack, type NavView } from "../../components/NavStack/NavStack";
import { Sheet } from "../../components/Sheet/Sheet";
import { useSelection } from "../../state/SelectionProvider";
import { AccuracyDetail } from "./AccuracyDetail";
import { NeighborhoodDetail } from "./NeighborhoodDetail";
import { RootView } from "./RootView";

const APP_TITLE = "Floodplain Creep";

type Detail = "accuracy" | null;

export function SheetPanel({ onOpenLimits }: { onOpenLimits: () => void }) {
  const { returnPeriod, year, neighborhoodId, selectNeighborhood } = useSelection();
  const summary = useCitySummary(returnPeriod);
  const neighborhoods = useNeighborhoods(returnPeriod, year);
  const [detail, setDetail] = useState<Detail>(null);
  const [expanded, setExpanded] = useState(false);

  const root: NavView = {
    key: "root",
    title: APP_TITLE,
    subtitle: summary.data?.city,
    content: <RootView onOpenAccuracy={() => setDetail("accuracy")} onOpenLimits={onOpenLimits} />,
  };
  const views: NavView[] = [root];
  if (neighborhoodId) {
    const name = neighborhoods.data?.features.find((feature) => feature.properties.neighborhood_id === neighborhoodId)
      ?.properties.name;
    views.push({
      key: `neighborhood-${neighborhoodId}`,
      title: name ?? "Neighborhood",
      content: <NeighborhoodDetail neighborhoodId={neighborhoodId} />,
    });
  } else if (detail === "accuracy") {
    views.push({ key: "accuracy", title: "Accuracy", content: <AccuracyDetail /> });
  }

  return (
    <Sheet label="Flood exposure" expanded={expanded} onToggleExpanded={() => setExpanded(!expanded)}>
      <NavStack
        views={views}
        onBack={() => {
          selectNeighborhood(null);
          setDetail(null);
        }}
      />
    </Sheet>
  );
}
