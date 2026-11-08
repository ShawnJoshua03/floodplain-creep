import { useValidation } from "../../api/hooks";
import { GroupedList, Row } from "../../components/GroupedList/GroupedList";
import { formatShare } from "../../lib/format";

interface AboutGroupProps {
  onOpenAccuracy: () => void;
  onOpenLimits: () => void;
}

export function AboutGroup({ onOpenAccuracy, onOpenLimits }: AboutGroupProps) {
  const validation = useValidation();
  const accuracy = validation.data?.accuracy.value;
  const value = accuracy === null || accuracy === undefined ? undefined : formatShare(accuracy);
  return (
    <GroupedList title="About this data">
      <Row label="Accuracy" value={value} onPress={onOpenAccuracy} />
      <Row label="Limits and misuse notice" onPress={onOpenLimits} />
    </GroupedList>
  );
}
