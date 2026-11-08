import { fireEvent, render, screen } from "@testing-library/react";
import { Sheet } from "./Sheet";

describe("Sheet", () => {
  it("is a named region that holds its content", () => {
    render(
      <Sheet label="Flood exposure" expanded={false} onToggleExpanded={() => undefined}>
        <p>Inside</p>
      </Sheet>,
    );
    expect(screen.getByRole("complementary", { name: "Flood exposure" })).toHaveTextContent("Inside");
  });

  it("names the grabber by the action it will take", () => {
    const onToggle = vi.fn();
    const { rerender } = render(
      <Sheet label="Panel" expanded={false} onToggleExpanded={onToggle}>
        <p>Inside</p>
      </Sheet>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Expand panel" }));
    expect(onToggle).toHaveBeenCalledTimes(1);
    rerender(
      <Sheet label="Panel" expanded onToggleExpanded={onToggle}>
        <p>Inside</p>
      </Sheet>,
    );
    expect(screen.getByRole("button", { name: "Collapse panel" })).toHaveAttribute("aria-expanded", "true");
  });
});
