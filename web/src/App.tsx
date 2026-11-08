import { useCitySummary } from "./api/hooks";
import { InlineMessage } from "./components/InlineMessage/InlineMessage";
import { AppShell } from "./features/shell/AppShell";
import styles from "./App.module.css";
import { SelectionProvider } from "./state/SelectionProvider";

const DEFAULT_RETURN_PERIOD = 100;

/** Waits for the city summary, which says which years exist, then starts on the last year. */
export function App() {
  const summary = useCitySummary(DEFAULT_RETURN_PERIOD);

  if (summary.isPending) {
    return (
      <main className={styles.centered}>
        <InlineMessage kind="loading">Loading Floodplain Creep</InlineMessage>
      </main>
    );
  }
  if (summary.isError) {
    return (
      <main className={styles.centered}>
        <InlineMessage kind="error" onRetry={() => void summary.refetch()}>
          Floodplain Creep could not reach its data.
        </InlineMessage>
      </main>
    );
  }
  return (
    <SelectionProvider initial={{ year: summary.data.last_year, returnPeriod: DEFAULT_RETURN_PERIOD }}>
      <AppShell />
    </SelectionProvider>
  );
}
