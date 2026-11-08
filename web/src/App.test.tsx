import { fireEvent, screen, within } from "@testing-library/react";
import { afterEach } from "vitest";
import { focusView } from "./testing/fixtures";
import { installFetch, renderApp } from "./testing/renderApp";
import { defaultRouter } from "./testing/routes";

vi.mock("./features/map/MapView", () => ({ MapView: () => <div data-testid="map" /> }));

afterEach(() => {
  vi.unstubAllGlobals();
});

async function ready() {
  return screen.findByRole("heading", { level: 1, name: "Badda" });
}

describe("start up", () => {
  it("shows a loading message while the first answer is pending", () => {
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
    expect(await ready()).toBeInTheDocument();
  });
});

describe("root view", () => {
  it("shows the neighborhood, the city, the scenarios, and the headline count with its change", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    expect(screen.getByText("Dhaka")).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "10-year" })).toBeChecked();
    expect(screen.getByText("Buildings in the modeled 10-year flood zone, 2023")).toBeInTheDocument();
    expect(screen.getByText("38,936")).toBeInTheDocument();
    expect(screen.getByText("+5,434 since 2018")).toBeInTheDocument();
  });

  it("shows the evidence rows and a sentence that says the growth is clear", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    expect(screen.getByText("+9.9%")).toBeInTheDocument();
    expect(screen.getByText("±4.7%")).toBeInTheDocument();
    expect(screen.getByText("2.1 times")).toBeInTheDocument();
    expect(screen.getByText("4.2 to 1")).toBeInTheDocument();
    expect(screen.getByText("1.4 to 1")).toBeInTheDocument();
    expect(screen.getByText(/The growth in Badda is 2.1 times the usual swing/)).toBeInTheDocument();
    expect(screen.getByText(/Other neighborhoods also gained buildings/)).toBeInTheDocument();
  });

  it("says plainly when the change is within noise", async () => {
    installFetch(defaultRouter({ "/focus": () => ({ body: focusView(10, { verdict: "within_noise" }) }) }));
    renderApp();
    await ready();
    expect(screen.getByText(/below the 2 times needed to call it clear/)).toBeInTheDocument();
  });

  it("says when there is not enough data to judge", async () => {
    installFetch(defaultRouter({ "/focus": () => ({ body: focusView(10, { verdict: "not_enough_data", withNoise: false }) }) }));
    renderApp();
    await ready();
    expect(screen.getByText(/not enough data to say whether the change in Badda/)).toBeInTheDocument();
    expect(screen.getByText("Not enough data to draw the usual yearly swing.")).toBeInTheDocument();
  });

  it("explains the minimum count when the selected year is suppressed", async () => {
    const counts = [33502, 33774, 35779, 35667, 34975, null];
    installFetch(defaultRouter({ "/focus": () => ({ body: focusView(10, { counts }) }) }));
    renderApp();
    await ready();
    expect(screen.getByText(/Fewer than 20 buildings are in the modeled flood zone in 2023/)).toBeInTheDocument();
    expect(screen.queryByText("38,936")).not.toBeInTheDocument();
  });

  it("shows the depth key with a person for scale, since the flood depth starts on", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    expect(await screen.findByText("0.1 to 0.5 m")).toBeInTheDocument();
    expect(screen.getByText("1.7 m")).toBeInTheDocument();
    expect(screen.getByText(/Modeled and approximate/)).toBeInTheDocument();
  });

  it("hides the depth key when the switch is turned off", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    fireEvent.click(screen.getByRole("switch", { name: "Show flood depth" }));
    expect(screen.queryByText("0.1 to 0.5 m")).not.toBeInTheDocument();
  });

  it("shows an error with Try again when the evidence fails after start up", async () => {
    const ok = defaultRouter();
    installFetch((url) =>
      url.pathname === "/focus" && url.searchParams.get("return_period") === "50" ? { status: 500 } : ok(url),
    );
    renderApp();
    await ready();
    fireEvent.click(screen.getByRole("radio", { name: "50-year" }));
    expect(await screen.findByText("The data did not load.")).toBeInTheDocument();
  });

  it("announces the neighborhood, year, and scenario politely when the year changes", async () => {
    const fetchMock = installFetch(defaultRouter());
    renderApp();
    await ready();
    fireEvent.change(screen.getByRole("slider", { name: "Year" }), { target: { value: "2020" } });
    expect(await screen.findByText(/^Badda, 2020, 10-year flood/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalled();
  });
});

describe("summary, accuracy, and limits", () => {
  it("says there is no written summary yet when none is stored", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    expect(await screen.findByText("No written summary yet.")).toBeInTheDocument();
  });

  it("shows the stored summary with its footnote", async () => {
    installFetch(defaultRouter({ "/brief": () => ({ body: { ...focusView(10), text: "Grew by 5,434.", source: "template" } }) }));
    renderApp();
    await ready();
    expect(await screen.findByText("Grew by 5,434.")).toBeInTheDocument();
    expect(screen.getByText("Written from a fixed template and the numbers above.")).toBeInTheDocument();
  });

  it("reads the stored accuracy result and says when labels are not checked by a person", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    fireEvent.click(await screen.findByRole("button", { name: /Accuracy/ }));
    expect(await screen.findByRole("heading", { level: 1, name: "Accuracy" })).toBeInTheDocument();
    expect(screen.getByText("55% (42% to 68%)")).toBeInTheDocument();
    expect(screen.getByText(/A person has not checked them yet/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Badda" }));
    expect(await ready()).toBeInTheDocument();
  });

  it("shows an error with Try again when the accuracy result does not load", async () => {
    installFetch(defaultRouter({ "/validation": () => ({ status: 500 }) }));
    renderApp();
    await ready();
    fireEvent.click(await screen.findByRole("button", { name: /Accuracy/ }));
    expect(await screen.findByText("The accuracy result did not load.")).toBeInTheDocument();
  });

  it("opens the limits and the misuse notice from the list row", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    const sheet = screen.getByRole("complementary", { name: "Flood exposure" });
    fireEvent.click(within(sheet).getByRole("button", { name: "Limits and misuse notice" }));
    const dialog = await screen.findByRole("dialog", { name: "Limits and misuse notice" });
    expect(await screen.findByText("This is not an official warning.")).toBeInTheDocument();
    expect(dialog).toHaveTextContent("preparedness and public accountability");
  });

  it("opens the limits from the info button", async () => {
    installFetch(defaultRouter());
    renderApp();
    await ready();
    const buttons = screen.getAllByRole("button", { name: "Limits and misuse notice" });
    fireEvent.click(buttons[0] as HTMLElement);
    expect(await screen.findByRole("dialog", { name: "Limits and misuse notice" })).toBeInTheDocument();
  });
});
