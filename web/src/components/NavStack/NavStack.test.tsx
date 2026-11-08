import { fireEvent, render, screen } from "@testing-library/react";
import { NavStack, type NavView } from "./NavStack";

const root: NavView = { key: "root", title: "Floodplain Creep", content: <p>Root content</p> };
const detail: NavView = { key: "n1", title: "Mirpur", content: <p>Detail content</p> };

describe("NavStack", () => {
  it("shows only the top view and no back button at the root", () => {
    render(<NavStack views={[root]} onBack={() => undefined} />);
    expect(screen.getByRole("heading", { name: "Floodplain Creep" })).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("labels the back button with the previous title and calls onBack", () => {
    const onBack = vi.fn();
    render(<NavStack views={[root, detail]} onBack={onBack} />);
    expect(screen.queryByText("Root content")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Floodplain Creep" }));
    expect(onBack).toHaveBeenCalledTimes(1);
  });

  it("moves focus to the new title after a push and after a pop", () => {
    const { rerender } = render(<NavStack views={[root]} onBack={() => undefined} />);
    rerender(<NavStack views={[root, detail]} onBack={() => undefined} />);
    expect(screen.getByRole("heading", { name: "Mirpur" })).toHaveFocus();
    rerender(<NavStack views={[root]} onBack={() => undefined} />);
    expect(screen.getByRole("heading", { name: "Floodplain Creep" })).toHaveFocus();
  });
});
