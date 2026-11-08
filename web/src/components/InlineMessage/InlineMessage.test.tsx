import { fireEvent, render, screen } from "@testing-library/react";
import { InlineMessage } from "./InlineMessage";

describe("InlineMessage", () => {
  it("shows a labeled activity indicator while loading", () => {
    render(<InlineMessage kind="loading">Loading neighborhoods</InlineMessage>);
    expect(screen.getByRole("status")).toHaveTextContent("Loading neighborhoods");
    expect(screen.getByRole("progressbar", { name: "Loading neighborhoods" })).toBeInTheDocument();
  });

  it("announces an error and offers Try again", () => {
    const onRetry = vi.fn();
    render(
      <InlineMessage kind="error" onRetry={onRetry}>
        The data did not load.
      </InlineMessage>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("The data did not load.");
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("shows an empty state with no button", () => {
    render(<InlineMessage kind="empty">Not enough data.</InlineMessage>);
    expect(screen.getByRole("status")).toHaveTextContent("Not enough data.");
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
