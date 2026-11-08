import { fireEvent, render, screen } from "@testing-library/react";
import { Scrubber } from "./Scrubber";

function renderScrubber(overrides: Partial<Parameters<typeof Scrubber>[0]> = {}) {
  const props = {
    label: "Year",
    min: 2018,
    max: 2023,
    value: 2020,
    playing: false,
    onChange: vi.fn(),
    onTogglePlay: vi.fn(),
    ...overrides,
  };
  render(<Scrubber {...props} />);
  return props;
}

describe("Scrubber", () => {
  it("shows the year and a range input named Year", () => {
    renderScrubber();
    expect(screen.getByRole("slider", { name: "Year" })).toHaveValue("2020");
    expect(screen.getByRole("status")).toHaveTextContent("2020");
  });

  it("reports a change of year", () => {
    const props = renderScrubber();
    fireEvent.change(screen.getByRole("slider", { name: "Year" }), { target: { value: "2021" } });
    expect(props.onChange).toHaveBeenCalledWith(2021);
  });

  it("names the play button by the action it will take", () => {
    const props = renderScrubber();
    fireEvent.click(screen.getByRole("button", { name: "Play" }));
    expect(props.onTogglePlay).toHaveBeenCalledTimes(1);
  });

  it("offers Pause while playing", () => {
    renderScrubber({ playing: true });
    expect(screen.getByRole("button", { name: "Pause" })).toBeInTheDocument();
  });
});
