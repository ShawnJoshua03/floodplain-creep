import { useFocus } from "./api/hooks";
import styles from "./App.module.css";
import { InlineMessage } from "./components/InlineMessage/InlineMessage";
import { AppShell } from "./features/shell/AppShell";
import { SelectionProvider } from "./state/SelectionProvider";

/** The app opens on the 10-year scenario, the ground that floods most often. The verdict is shown for every scenario. */
const OPENING_RETURN_PERIOD = 10;

/** Waits for the first answer, which says which years and scenarios exist, then starts on the last year. */
export function App() {
  const focus = useFocus(OPENING_RETURN_PERIOD);

  if (focus.isPending) {
    return (
      <main className={styles.centered}>
        <InlineMessage kind="loading">Loading Floodplain Creep</InlineMessage>
      </main>
    );
  }
  if (focus.isError) {
    return (
      <main className={styles.centered}>
        <InlineMessage kind="error" onRetry={() => void focus.refetch()}>
          Floodplain Creep could not reach its data.
        </InlineMessage>
      </main>
    );
  }
  const view = focus.data;
  return (
    <SelectionProvider
      initial={{
        year: view.last_year,
        returnPeriod: OPENING_RETURN_PERIOD,
        overlayOn: true,
        returnPeriods: view.return_periods,
        focusName: view.neighborhood.name,
        city: view.city,
      }}
    >
      <AppShell />
    </SelectionProvider>
  );
}
