import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach } from "vitest";
import { focusView } from "./testing/fixtures";
import { installFetch, renderApp } from "./testing/renderApp";
import { defaultRouter } from "./testing/routes";

vi.mock("./features/map/MapView", () => ({ MapView: () => <div data-testid="map" /> }));

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("rapid selection", () => {
  it("keeps the latest scenario when an earlier response arrives late", async () => {
    let release: () => void = () => undefined;
    const slow = new Promise<void>((resolve) => {
      release = resolve;
    });
    installFetch(
      defaultRouter({
        "/focus": (url) => {
          const returnPeriod = Number(url.searchParams.get("return_period"));
          if (returnPeriod === 50) {
            return { body: focusView(50, { counts: [1000, 1000, 1000, 1000, 1000, 11111] }), after: slow };
          }
          return { body: focusView(returnPeriod) };
        },
      }),
    );
    renderApp();
    await screen.findByRole("heading", { level: 1, name: "Badda" });
    fireEvent.click(screen.getByRole("radio", { name: "50-year" }));
    fireEvent.click(screen.getByRole("radio", { name: "100-year" }));
    expect(await screen.findByText("Buildings in the modeled 100-year flood zone, 2023")).toBeInTheDocument();

    release();
    await waitFor(() => expect(screen.getByRole("radio", { name: "100-year" })).toBeChecked());
    expect(screen.getByText("Buildings in the modeled 100-year flood zone, 2023")).toBeInTheDocument();
    expect(screen.queryByText("11,111")).not.toBeInTheDocument();
  });
});
