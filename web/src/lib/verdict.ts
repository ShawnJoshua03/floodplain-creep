import type { FocusView } from "../api/types";

type Balance = NonNullable<FocusView["balance"]>;

const ONE_DECIMAL = new Intl.NumberFormat("en", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const WHOLE = new Intl.NumberFormat("en", { maximumFractionDigits: 0 });

/** Gaining areas for each losing area, for example "4.2 to 1". Null when nothing was lost. */
export function ratioText(gaining: number, losing: number): string | null {
  return losing === 0 ? null : `${ONE_DECIMAL.format(gaining / losing)} to 1`;
}

/** The one sentence a visitor should take away, written from the computed numbers only. */
export function takeawaySentence(view: FocusView): string {
  const { signal } = view;
  const name = view.neighborhood.name;
  const zone = `${name}'s ${view.return_period}-year flood zone`;
  if (signal.verdict === "not_enough_data" || signal.times_typical_swing === null) {
    return `There is not enough data to judge the change in ${zone}.`;
  }
  const last = view.series.find((row) => row.year === view.last_year);
  const change = last?.growth_pct ?? signal.smoothed_change_pct;
  const times = ONE_DECIMAL.format(signal.times_typical_swing);
  if (change === null || change === undefined) {
    return `There is not enough data to judge the change in ${zone}.`;
  }
  const size = WHOLE.format(Math.abs(change));
  if (signal.verdict === "within_noise") {
    const sign = change < 0 ? "−" : "+";
    return `Buildings in ${zone} changed by ${sign}${size}% since ${view.first_year}. That is within the usual yearly swing, so it is not clearly real.`;
  }
  const verb = signal.verdict === "clear_growth" ? "grew" : "fell";
  return `Buildings in ${zone} ${verb} ${size}% since ${view.first_year}. That is ${times} times the usual yearly swing.`;
}

/** How the areas that gained compare with the areas that lost, here and in the rest of the city. */
export function balanceSentence(name: string, balance: Balance | null): string | null {
  if (!balance) {
    return null;
  }
  const here = ratioText(balance.focus.cells_gaining, balance.focus.cells_losing);
  const rest = ratioText(balance.rest_of_city.cells_gaining, balance.rest_of_city.cells_losing);
  if (!here || !rest) {
    return null;
  }
  return `Areas of 100 m that gained ${balance.threshold_buildings} or more buildings outnumber those that lost that many by ${here} in ${name}, against ${rest} in the rest of the city.`;
}

export function otherNeighborhoodsNote(name: string): string {
  return `Other neighborhoods also gained buildings. ${name} is shown because it is the largest case.`;
}
