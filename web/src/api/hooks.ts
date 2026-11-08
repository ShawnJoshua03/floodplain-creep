import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getJson, isNotFound } from "./client";
import type {
  Brief,
  CitySummary,
  Limits,
  NeighborhoodCollection,
  OverlayInfo,
  ValidationResult,
} from "./types";

export function useCitySummary(returnPeriod: number) {
  return useQuery({
    queryKey: ["city-summary", returnPeriod],
    queryFn: ({ signal }) => getJson<CitySummary>("/city/summary", { return_period: returnPeriod }, signal),
    placeholderData: keepPreviousData,
  });
}

export function useNeighborhoods(returnPeriod: number, year: number) {
  return useQuery({
    queryKey: ["neighborhoods", returnPeriod, year],
    queryFn: ({ signal }) =>
      getJson<NeighborhoodCollection>("/neighborhoods", { return_period: returnPeriod, year }, signal),
    placeholderData: keepPreviousData,
  });
}

export function useOverlay(returnPeriod: number, enabled: boolean) {
  return useQuery({
    queryKey: ["overlay", returnPeriod],
    queryFn: ({ signal }) => getJson<OverlayInfo>("/hazard/overlay", { return_period: returnPeriod }, signal),
    enabled,
  });
}

export function useValidation() {
  return useQuery({
    queryKey: ["validation"],
    queryFn: ({ signal }) => getJson<ValidationResult>("/validation", undefined, signal),
  });
}

export function useLimits(enabled: boolean) {
  return useQuery({
    queryKey: ["limits"],
    queryFn: ({ signal }) => getJson<Limits>("/limits", undefined, signal),
    enabled,
  });
}

/** A missing brief is a normal answer, so it resolves to null instead of an error. */
export function useBrief(neighborhoodId: string, returnPeriod: number) {
  return useQuery({
    queryKey: ["brief", neighborhoodId, returnPeriod],
    queryFn: async ({ signal }) => {
      try {
        return await getJson<Brief>(`/brief/${neighborhoodId}`, { return_period: returnPeriod }, signal);
      } catch (error) {
        if (isNotFound(error)) {
          return null;
        }
        throw error;
      }
    },
  });
}
