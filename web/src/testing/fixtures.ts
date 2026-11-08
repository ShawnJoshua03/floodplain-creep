import type {
  Brief,
  CitySummary,
  Limits,
  NeighborhoodCollection,
  OverlayInfo,
  ValidationResult,
} from "../api/types";

const POLYGON = { type: "Polygon" as const, coordinates: [[[0, 0], [1, 0], [1, 1], [0, 0]]] };

interface Seed {
  id: string;
  name: string;
  count: number | null;
}

const SEEDS: Seed[] = [
  { id: "n1", name: "Adabor", count: 6802 },
  { id: "n2", name: "Badda", count: 5400 },
  { id: "n3", name: "Dhanmondi", count: null },
  { id: "n4", name: "Gulshan", count: 4100 },
  { id: "n5", name: "Hazaribagh", count: 3900 },
  { id: "n6", name: "Khilgaon", count: 3300 },
  { id: "n7", name: "Lalbagh", count: 2500 },
  { id: "n8", name: "Mirpur", count: 1900 },
];

export function neighborhoods(year: number, returnPeriod: number, seeds: Seed[] = SEEDS): NeighborhoodCollection {
  return {
    type: "FeatureCollection",
    year,
    return_period: returnPeriod,
    features: seeds.map(({ id, name, count }) => ({
      type: "Feature",
      geometry: POLYGON,
      properties: {
        neighborhood_id: id,
        name,
        year,
        return_period: returnPeriod,
        boundary_source: "test",
        buildings_in_zone: count,
        new_buildings_in_zone: count === null ? null : -496,
        growth_pct: count === null ? null : -6.8,
        suppressed: count === null,
        change_available: count !== null,
      },
    })),
  };
}

export function citySummary(returnPeriod: number, newBuildings: number): CitySummary {
  return {
    city: "Dhaka",
    return_period: returnPeriod,
    first_year: 2018,
    last_year: 2023,
    return_periods: [10, 50, 100, 500],
    min_count_k: 20,
    years: [2018, 2019, 2020, 2021, 2022, 2023].map((year) => ({
      year,
      buildings_in_zone: 100000,
      new_buildings_in_zone: newBuildings,
      neighborhoods_shown: 24,
      neighborhoods_suppressed: 9,
    })),
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

export const BRIEF: Brief = {
  neighborhood_id: "n1",
  return_period: 100,
  text: "Buildings in the modeled flood zone fell by 496 since 2018.",
  source: "template",
};
