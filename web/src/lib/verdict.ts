import type { FocusView } from "../api/types";

type Signal = FocusView["signal"];
type Balance = NonNullable<FocusView["balance"]>;

const ONE_DECIMAL = new Intl.NumberFormat("en", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** Gaining areas for each losing area, for example "4.2 to 1". Null when nothing was lost. */
export function ratioText(gaining: number, losing: number): string | null {
  return losing === 0 ? null : `${ONE_DECIMAL.format(gaining / losing)} to 1`;
}

/** One plain sentence about the change, written from the computed numbers only. */
export function verdictSentence(name: string, signal: Signal, balance: Balance | null): string {
  if (signal.verdict === "not_enough_data" || signal.times_typical_swing === null) {
    return `There is not enough data to say whether the change in ${name} stands out from noise.`;
  }
  const times = ONE_DECIMAL.format(signal.times_typical_swing);
  if (signal.verdict === "within_noise") {
    return `The change in ${name} is ${times} times the usual swing, below the ${signal.required_multiple} times needed to call it clear.`;
  }
  const direction = signal.verdict === "clear_growth" ? "growth" : "decline";
  const ratio = balance ? ratioText(balance.focus.cells_gaining, balance.focus.cells_losing) : null;
  const support = ratio ? ` Areas gaining buildings outnumber areas losing them by ${ratio}.` : "";
  return `The ${direction} in ${name} is ${times} times the usual swing.${support}`;
}

export function otherNeighborhoodsNote(name: string): string {
  return `Other neighborhoods also gained buildings. ${name} is shown because it is the largest case.`;
}
