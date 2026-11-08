import { AboutGroup } from "./AboutGroup";
import { CityTotals } from "./CityTotals";
import { NeighborhoodList } from "./NeighborhoodList";
import { OverlayControls } from "./OverlayControls";
import styles from "./RootView.module.css";

interface RootViewProps {
  onOpenAccuracy: () => void;
  onOpenLimits: () => void;
}

export function RootView({ onOpenAccuracy, onOpenLimits }: RootViewProps) {
  return (
    <div className={styles.root}>
      <CityTotals />
      <OverlayControls />
      <NeighborhoodList />
      <AboutGroup onOpenAccuracy={onOpenAccuracy} onOpenLimits={onOpenLimits} />
    </div>
  );
}
