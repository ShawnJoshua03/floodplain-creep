import { fireEvent, screen, within } from "@testing-library/react";
import { afterEach } from "vitest";
import { neighborhoods } from "./testing/fixtures";
import { installFetch, renderApp } from "./testing/renderApp";
import { defaultRouter } from "./testing/routes";

vi.mock("./features/map/MapView", () => ({ MapView: () => <div data-testid="map" /> }));

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("start up", () => {
  it("shows a loading message while the city summary is pending", () => {
    installFetch(() => ({ after: new Promise<void>(() => undefined) }));
    renderApp();
    expect(screen.getByRole("status")).toHaveTextContent("Loading Floodplain Creep");
  });

  it("shows one plain sentence and Try again when the data cannot be reached", async () => {
    let failing = true;
    const ok = defaultRouter();
    installFetch((url) => (failing ? { status: 500 } : ok(url)));
    renderApp();
    expect(await screen.findByRole("alert")).toHaveTextContent("could not reach its data");
    failing = false;
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByRole("heading", { level: 1, name: "Floodplain Creep" })).toBeInTheDocument();
  });
});

describe("root view", () => {
  it("shows the title, city, scenario control, and the new-building total with its sign", async () => {
    installFetch(defaultRouter());
    renderApp();
    expect(await screen.findByRole("heading", { level: 1, name: "Floodplain Creep" })).toBeInTheDocument();
    expect(screen.getByText("Dhaka")).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "100-year" })).toBeChecked();
    expect(screen.getByText("New buildings in the modeled flood zone since 2018")).toBeInTheDocument();
    expect(screen.getByText("+1,234")).toBeInTheDocument();
  });

  it("lists the six highest neighborhoods, then everything including not enough data", async () => {
    installFetch(defaultRouter());
    renderApp();
    const heading = await screen.findByRole("heading", { name: "Neighborhoods" });
    const section = heading.closest("section") as HTMLElement;
    expect(within(section).getAllByRole("button")).toHaveLength(7);
    expect(screen.queryByText("Mirpur")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Show all" }));
    expect(screen.getByRole("button", { name: /Dhanmondi/ })).toHaveTextContent("Not enough data");
    expect(screen.getByRole("button", { name: /Mirpur/ })).toBeInTheDocument();
  });

  it("shows an empty state when there are no neighborhoods", async () => {
    installFetch(defaultRouter({ "/neighborhoods": () => ({ body: neighborhoods(2023, 100, []) }) }));
    renderApp();
    expect(await screen.findByText("No neighborhoods to show.")).toBeInTheDocument();
  });

  it("shows an error with Try again when the neighborhoods fail", async () => {
    installFetch(defaultRouter({ "/neighborhoods": () => ({ status: 500 }) }));
    renderApp();
    expect(await screen.findByText("The neighborhoods did not load.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Try again" }).length).toBeGreaterThan(0);
  });

  it("shows the depth key with a person for scale when flood depth is switched on", async () => {
    installFetch(defaultRouter());
    renderApp();
    fireEvent.click(await screen.findByRole("switch", { name: "Show flood depth" }));
    expect(await screen.findByText("0.1 to 0.5 m")).toBeInTheDocument();
    expect(screen.getByText("1.7 m")).toBeInTheDocument();
    expect(screen.getByText(/Modeled and approximate/)).toBeInTheDocument();
  });

  it("announces the year and scenario politely when the year changes", async () => {
    const fetchMock = installFetch(defaultRouter());
    renderApp();
    fireEvent.change(await screen.findByRole("slider", { name: "Year" }), { target: { value: "2020" } });
    expect(await screen.findByText(/^2020, 100-year flood/)).toBeInTheDocument();
    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(urls.some((url) => url.includes("year=2020"))).toBe(true);
  });
});
