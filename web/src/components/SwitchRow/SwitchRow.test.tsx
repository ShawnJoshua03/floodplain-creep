import { fireEvent, render, screen } from "@testing-library/react";
import { SwitchRow } from "./SwitchRow";

describe("SwitchRow", () => {
  it("is a switch named by its label and reflects its state", () => {
    render(<SwitchRow label="Show flood depth" checked onChange={() => undefined} />);
    expect(screen.getByRole("switch", { name: "Show flood depth" })).toBeChecked();
  });

  it("reports the new state when pressed", () => {
    const onChange = vi.fn();
    render(<SwitchRow label="Show flood depth" checked={false} onChange={onChange} />);
    fireEvent.click(screen.getByRole("switch", { name: "Show flood depth" }));
    expect(onChange).toHaveBeenCalledWith(true);
  });
});
