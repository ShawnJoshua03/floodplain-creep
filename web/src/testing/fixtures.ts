import type { FocusView, GrowthInfo, Limits, OverlayInfo, ValidationResult } from "../api/types";

const POLYGON = { type: "Polygon" as const, coordinates: [[[0, 0], [1, 0], [1, 1], [0, 0]]] };

const FOCUS_COUNTS = [33502, 33774, 35779, 35667, 34975, 38936];

interface FocusOptions {
  counts?: (number | null)[];
  verdict?: FocusView["signal"]["verdict"];
  withNoise?: boolean;
}

/** A focus answer for one scenario. Suppressed years hold null counts, as in the real API. */
export function focusView(returnPeriod: number, options: FocusOptions = {}): FocusView {
  const { counts = FOCUS_COUNTS, verdict = "clear_growth", withNoise = true } = options;
  const first = counts[0] ?? null;
  return {
    city: "Dhaka",
    return_period: returnPeriod,
    return_periods: [10, 50, 100, 500],
    first_year: 2018,
    last_year: 2023,
    min_count_k: 20,
    neighborhood: { neighborhood_id: "n1", name: "Badda", boundary_source: "test", coverage: 0.943, geometry: POLYGON },
    series: counts.map((count, index) => ({
      year: 2018 + index,
      buildings_in_zone: count,
      new_buildings_in_zone: count === null || first === null ? null : count - first,
      growth_pct: count === null || first === null ? null : Math.round(((count - first) / first) * 1000) / 10,
      suppressed: count === null,
      change_available: count !== null && first !== null,
    })),
    noise: withNoise ? { typical_swing_pct: 4.7, neighborhoods_used: 23 } : null,
    signal:
      verdict === "not_enough_data"
        ? { verdict, smoothed_change_pct: null, times_typical_swing: null, required_multiple: 2 }
        : { verdict, smoothed_change_pct: 9.9, times_typical_swing: verdict === "within_noise" ? 1.5 : 2.1, required_multiple: 2 },
    balance: {
      threshold_buildings: 5,
      focus: { cells_gaining: 595, cells_losing: 141 },
      rest_of_city: { cells_gaining: 1188, cells_losing: 854 },
    },
  };
}

export const OVERLAY: OverlayInfo = {
  return_period: 100,
  image_url: "/overlays/depth_rp100.png",
  bounds: [90.34, 23.69, 90.47, 23.82],
  bins: [
    { min_depth_m: 0.1, max_depth_m: 0.5, color: "var(--ramp-depth-1)" },
    { min_depth_m: 2, max_depth_m: null, color: "var(--ramp-depth-4)" },
  ],
  label: "Modeled river flood depth. Simulated scenario, not a forecast.",
};

export const GROWTH: GrowthInfo = {
  return_period: 100,
  bounds: [90.34, 23.69, 90.47, 23.82],
  block_m: 500,
  bins: [
    { min_buildings: 20, max_buildings: 80, color: "var(--ramp-growth-1)" },
    { min_buildings: 80, max_buildings: null, color: "var(--ramp-growth-4)" },
  ],
  image_urls: { "2018": "/overlays/growth_rp100_2018.png", "2023": "/overlays/growth_rp100_2023.png" },
  label: "Buildings in the modeled flood zone, blended from blocks. Blocks with too few buildings are hidden.",
};

export const VALIDATION: ValidationResult = {
  labeled_cells: 140,
  excluded_unclear: 3,
  tuning_cells: 84,
  test_cells: 56,
  change_threshold_buildings: 1.8,
  confusion: { tp: 9, fp: 21, fn: 4, tn: 22 },
  accuracy: { value: 0.5535, low: 0.424, high: 0.676, n: 56 },
  precision: { value: 0.3, low: 0.167, high: 0.479, n: 30 },
  recall: { value: 0.692, low: 0.424, high: 0.873, n: 13 },
  sampling_note: "Test sampling note.",
  label_sources: { human: 0, audit: 0, ai: 140 },
  ai_human_agreement: { value: null, low: null, high: null, n: 0 },
  imagery_source: "Test imagery",
  imagery_dates: "Test dates",
  start_year: 2018,
  end_year: 2023,
  created_at: "2026-11-07T00:00:00Z",
};

export const LIMITS: Limits = {
  limits: ["Data covers 2018 to 2023.", "This is not an official warning."],
  misuse_notice: "This tool is for preparedness and public accountability.",
  banned_terms: ["example term"],
};
