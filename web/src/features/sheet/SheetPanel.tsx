import { useState } from "react";
import { NavStack, type NavView } from "../../components/NavStack/NavStack";
import { Sheet } from "../../components/Sheet/Sheet";
import { useSelection } from "../../state/SelectionProvider";
import { AccuracyDetail } from "./AccuracyDetail";
import { RootView } from "./RootView";

export function SheetPanel({ onOpenLimits }: { onOpenLimits: () => void }) {
  const { focusName, city } = useSelection();
  const [accuracyOpen, setAccuracyOpen] = useState(false);

  const views: NavView[] = [
    {
      key: "root",
      title: focusName,
      subtitle: city,
      content: <RootView onOpenAccuracy={() => setAccuracyOpen(true)} onOpenLimits={onOpenLimits} />,
    },
  ];
  if (accuracyOpen) {
    views.push({ key: "accuracy", title: "Accuracy", content: <AccuracyDetail /> });
  }
  return (
    <Sheet label="Flood exposure">
      <NavStack views={views} onBack={() => setAccuracyOpen(false)} />
    </Sheet>
  );
}
