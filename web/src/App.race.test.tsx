import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach } from "vitest";
import { citySummary } from "./testing/fixtures";
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
        "/city/summary": (url) => {
          const returnPeriod = Number(url.searchParams.get("return_period"));
          if (returnPeriod === 10) {
            return { body: citySummary(10, 111), after: slow };
          }
          return { body: citySummary(returnPeriod, returnPeriod === 50 ? 777 : 1234) };
        },
      }),
    );
    renderApp();
    fireEvent.click(await screen.findByRole("radio", { name: "10-year" }));
    fireEvent.click(screen.getByRole("radio", { name: "50-year" }));
    expect(await screen.findByText("+777")).toBeInTheDocument();

    release();
    await waitFor(() => expect(screen.getByRole("radio", { name: "50-year" })).toBeChecked());
    expect(screen.getByText("+777")).toBeInTheDocument();
    expect(screen.queryByText("+111")).not.toBeInTheDocument();
  });
});
