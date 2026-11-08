import { fireEvent, render, screen } from "@testing-library/react";
import { SegmentedControl } from "./SegmentedControl";

const options = [
  { value: 10, label: "10 yr" },
  { value: 50, label: "50 yr" },
  { value: 100, label: "100 yr" },
];

describe("SegmentedControl", () => {
  it("is a named group of radio options with the current one checked", () => {
    render(<SegmentedControl label="Flood scenario" options={options} value={50} onChange={() => undefined} />);
    expect(screen.getByRole("group", { name: "Flood scenario" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "50 yr" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "10 yr" })).not.toBeChecked();
  });

  it("reports a click", () => {
    const onChange = vi.fn();
    render(<SegmentedControl label="Flood scenario" options={options} value={10} onChange={onChange} />);
    fireEvent.click(screen.getByRole("radio", { name: "100 yr" }));
    expect(onChange).toHaveBeenCalledWith(100);
  });

  it("moves with the arrow keys and wraps around", () => {
    const onChange = vi.fn();
    render(<SegmentedControl label="Flood scenario" options={options} value={100} onChange={onChange} />);
    const last = screen.getByRole("radio", { name: "100 yr" });
    fireEvent.keyDown(last, { key: "ArrowRight" });
    expect(onChange).toHaveBeenLastCalledWith(10);
    fireEvent.keyDown(last, { key: "ArrowLeft" });
    expect(onChange).toHaveBeenLastCalledWith(50);
  });
});
