import { focusView, GROWTH, LIMITS, OVERLAY, VALIDATION } from "./fixtures";
import type { MockReply, Router } from "./renderApp";

/** Every endpoint answers with fixtures. A missing brief is a 404, as in the real API. */
export function defaultRouter(overrides: Record<string, Router> = {}): Router {
  return (url) => {
    const override = overrides[url.pathname];
    if (override) {
      return override(url);
    }
    const returnPeriod = Number(url.searchParams.get("return_period") ?? 10);
    const replies: Record<string, MockReply> = {
      "/focus": { body: focusView(returnPeriod) },
      "/validation": { body: VALIDATION },
      "/limits": { body: LIMITS },
      "/hazard/overlay": { body: OVERLAY },
      "/hazard/growth": { body: GROWTH },
    };
    return replies[url.pathname] ?? { status: 404, body: { detail: "Not found" } };
  };
}

