import { fireEvent, screen, within } from "@testing-library/react";
import { afterEach } from "vitest";
import { BRIEF } from "./testing/fixtures";
import { installFetch, renderApp } from "./testing/renderApp";
import { defaultRouter } from "./testing/routes";

vi.mock("./features/map/MapView", () => ({ MapView: () => <div data-testid="map" /> }));

afterEach(() => {
  vi.unstubAllGlobals();
});

async function openNeighborhood(name: RegExp) {
  fireEvent.click(await screen.findByRole("button", { name }));
}

describe("neighborhood detail", () => {
  it("shows the counts, a decrease with its minus sign, and a note when there is no summary yet", async () => {
    installFetch(defaultRouter());
    renderApp();
    await openNeighborhood(/Adabor/);
    expect(await screen.findByRole("heading", { level: 1, name: "Adabor" })).toBeInTheDocument();
    expect(screen.getByText("6,802")).toBeInTheDocument();
    expect(screen.getByText("−496")).toBeInTheDocument();
    expect(screen.getByText("−6.8%")).toBeInTheDocument();
    expect(await screen.findByText("No written summary yet.")).toBeInTheDocument();
  });

  it("shows the stored summary with its footnote", async () => {
    installFetch(defaultRouter({ "/brief/n1": () => ({ body: BRIEF }) }));
    renderApp();
    await openNeighborhood(/Adabor/);
    expect(await screen.findByText(BRIEF.text)).toBeInTheDocument();
    expect(screen.getByText("Written from a fixed template and the numbers above.")).toBeInTheDocument();
  });

  it("explains the minimum count for a suppressed neighborhood and shows no numbers", async () => {
    installFetch(defaultRouter());
    renderApp();
    fireEvent.click(await screen.findByRole("button", { name: "Show all" }));
    await openNeighborhood(/Dhanmondi/);
    expect(await screen.findByText(/Fewer than 20 buildings/)).toBeInTheDocument();
    expect(screen.getAllByText("Not available")).toHaveLength(3);
  });

  it("goes back to the root view, which is named by the back button", async () => {
    installFetch(defaultRouter());
    renderApp();
    await openNeighborhood(/Adabor/);
    fireEvent.click(await screen.findByRole("button", { name: "Floodplain Creep" }));
    expect(await screen.findByRole("heading", { level: 1, name: "Floodplain Creep" })).toBeInTheDocument();
  });
});

describe("accuracy detail", () => {
  it("reads the stored result and says when labels are not checked by a person", async () => {
    installFetch(defaultRouter());
    renderApp();
    fireEvent.click(await screen.findByRole("button", { name: /Accuracy/ }));
    expect(await screen.findByRole("heading", { level: 1, name: "Accuracy" })).toBeInTheDocument();
    expect(screen.getByText("55% (42% to 68%)")).toBeInTheDocument();
    expect(screen.getByText("30% (17% to 48%)")).toBeInTheDocument();
    expect(screen.getByText("Test sampling note.")).toBeInTheDocument();
    expect(screen.getByText(/A person has not checked them yet/)).toBeInTheDocument();
  });

  it("shows an error with Try again when the result does not load", async () => {
    installFetch(defaultRouter({ "/validation": () => ({ status: 500 }) }));
    renderApp();
    fireEvent.click(await screen.findByRole("button", { name: /Accuracy/ }));
    expect(await screen.findByText("The accuracy result did not load.")).toBeInTheDocument();
  });
});

describe("limits dialog", () => {
  it("opens from the list row with the limits and the misuse notice", async () => {
    installFetch(defaultRouter());
    renderApp();
    const sheet = await screen.findByRole("complementary", { name: "Flood exposure" });
    fireEvent.click(within(sheet).getByRole("button", { name: "Limits and misuse notice" }));
    const dialog = await screen.findByRole("dialog", { name: "Limits and misuse notice" });
    expect(await screen.findByText("This is not an official warning.")).toBeInTheDocument();
    expect(dialog).toHaveTextContent("preparedness and public accountability");
  });

  it("opens from the info button", async () => {
    installFetch(defaultRouter());
    renderApp();
    await screen.findByRole("heading", { level: 1, name: "Floodplain Creep" });
    const buttons = screen.getAllByRole("button", { name: "Limits and misuse notice" });
    fireEvent.click(buttons[0] as HTMLElement);
    expect(await screen.findByRole("dialog", { name: "Limits and misuse notice" })).toBeInTheDocument();
  });
});
