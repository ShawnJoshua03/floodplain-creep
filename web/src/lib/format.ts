const COUNT = new Intl.NumberFormat("en");
const SIGNED = new Intl.NumberFormat("en", { signDisplay: "exceptZero" });
const PERCENT = new Intl.NumberFormat("en", { style: "percent", maximumFractionDigits: 0 });
const PERCENT_ONE_DECIMAL = new Intl.NumberFormat("en", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
  signDisplay: "exceptZero",
});

export const NOT_ENOUGH_DATA = "Not enough data";

export function formatCount(value: number): string {
  return COUNT.format(value);
}

/** A decrease is real data, so it keeps its minus sign. */
export function formatSigned(value: number): string {
  return SIGNED.format(value).replace("-", "−");
}

export function formatGrowth(value: number): string {
  return `${PERCENT_ONE_DECIMAL.format(value).replace("-", "−")}%`;
}

export function formatShare(value: number): string {
  return PERCENT.format(value);
}

interface Interval {
  value: number | null;
  low: number | null;
  high: number | null;
}

export const NOT_AVAILABLE = "Not available";

/** A share with its 95 percent range, for example "55% (42% to 68%)". */
export function formatInterval(interval: Interval): string {
  if (interval.value === null) {
    return NOT_AVAILABLE;
  }
  const range =
    interval.low === null || interval.high === null
      ? ""
      : ` (${formatShare(interval.low)} to ${formatShare(interval.high)})`;
  return `${formatShare(interval.value)}${range}`;
}
