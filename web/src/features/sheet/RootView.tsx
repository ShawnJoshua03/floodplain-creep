import { SegmentedControl } from "../../components/SegmentedControl/SegmentedControl";
import { scenarioNote } from "../../lib/scenarios";
import { useSelection } from "../../state/SelectionProvider";
import { AboutGroup } from "./AboutGroup";
import { BriefSection } from "./BriefSection";
import { FocusBody } from "./FocusBody";
import { OverlayControls } from "./OverlayControls";
import styles from "./RootView.module.css";

interface RootViewProps {
  onOpenAccuracy: () => void;
  onOpenLimits: () => void;
}

export function RootView({ onOpenAccuracy, onOpenLimits }: RootViewProps) {
  const { returnPeriod, returnPeriods, setReturnPeriod } = useSelection();
  const options = returnPeriods.map((value) => ({ value, label: `${value}-year` }));
  return (
    <div className={styles.root}>
      <div className={styles.scenario}>
        <SegmentedControl label="Flood scenario" options={options} value={returnPeriod} onChange={setReturnPeriod} />
        <p className={styles.note}>{scenarioNote(returnPeriod)}</p>
      </div>
      <FocusBody />
      <OverlayControls />
      <BriefSection />
      <AboutGroup onOpenAccuracy={onOpenAccuracy} onOpenLimits={onOpenLimits} />
    </div>
  );
}
