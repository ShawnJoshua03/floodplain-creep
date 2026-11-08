import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { App } from "../App";

export interface MockReply {
  status?: number;
  body?: object;
  /** Hold the reply until this promise settles, to model a slow response. */
  after?: Promise<void>;
}

export type Router = (url: URL) => MockReply;

/** Replaces fetch with a router, so tests run against fixtures and never the network. */
export function installFetch(router: Router): ReturnType<typeof vi.fn> {
  const mock = vi.fn(async (input: RequestInfo | URL) => {
    const reply = router(new URL(String(input), "http://localhost"));
    await reply.after;
    const status = reply.status ?? 200;
    return new Response(JSON.stringify(reply.body ?? {}), { status });
  });
  vi.stubGlobal("fetch", mock);
  return mock;
}

export function renderApp() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>,
  );
}
