import { useQuery } from "@tanstack/react-query";
import { getJson, isNotFound } from "./client";
import type { Brief, FocusView, Limits, OverlayInfo, ValidationResult } from "./types";

/** No placeholder data: a new scenario shows a loading state, never the previous scenario's numbers. */
export function useFocus(returnPeriod: number) {
  return useQuery({
    queryKey: ["focus", returnPeriod],
    queryFn: ({ signal }) => getJson<FocusView>("/focus", { return_period: returnPeriod }, signal),
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
export function useBrief(returnPeriod: number) {
  return useQuery({
    queryKey: ["brief", returnPeriod],
    queryFn: async ({ signal }) => {
      try {
        return await getJson<Brief>("/brief", { return_period: returnPeriod }, signal);
      } catch (error) {
        if (isNotFound(error)) {
          return null;
        }
        throw error;
      }
    },
  });
}
