import { BRIEF, citySummary, LIMITS, neighborhoods, OVERLAY, VALIDATION } from "./fixtures";
import type { MockReply, Router } from "./renderApp";

/** Every endpoint answers with fixtures. A missing brief is a 404, as in the real API. */
export function defaultRouter(overrides: Record<string, Router> = {}): Router {
  return (url) => {
    const override = overrides[url.pathname];
    if (override) {
      return override(url);
    }
    const returnPeriod = Number(url.searchParams.get("return_period") ?? 100);
    const year = Number(url.searchParams.get("year") ?? 2023);
    const replies: Record<string, MockReply> = {
      "/city/summary": { body: citySummary(returnPeriod, 1234) },
      "/neighborhoods": { body: neighborhoods(year, returnPeriod) },
      "/validation": { body: VALIDATION },
      "/limits": { body: LIMITS },
      "/hazard/overlay": { body: OVERLAY },
      "/brief/n9": { body: BRIEF },
    };
    return replies[url.pathname] ?? { status: 404, body: { detail: "Not found" } };
  };
}
