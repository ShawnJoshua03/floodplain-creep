import { useOverlay } from "../../api/hooks";
import { InlineMessage } from "../../components/InlineMessage/InlineMessage";
import { SwitchRow } from "../../components/SwitchRow/SwitchRow";
import { useSelection } from "../../state/SelectionProvider";

/** The switch for the flood depth layer. The legend for its colors sits beside the map. */
export function OverlayControls() {
  const { returnPeriod, overlayOn, setOverlay } = useSelection();
  const query = useOverlay(returnPeriod, overlayOn);

  return (
    <>
      <SwitchRow label="Show flood depth" checked={overlayOn} onChange={setOverlay} />
      {overlayOn && query.isPending ? <InlineMessage kind="loading">Loading flood depth</InlineMessage> : null}
      {overlayOn && query.isError ? (
        <InlineMessage kind="error" onRetry={() => void query.refetch()}>
          The flood depth layer did not load.
        </InlineMessage>
      ) : null}
    </>
  );
}
