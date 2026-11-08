import { fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { Dialog } from "./Dialog";

function Harness() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>
        Open limits
      </button>
      <Dialog open={open} title="Limits and misuse notice" onClose={() => setOpen(false)}>
        <p>Not an official warning.</p>
      </Dialog>
    </>
  );
}

describe("Dialog", () => {
  it("opens as a named dialog holding its content", () => {
    render(<Harness />);
    fireEvent.click(screen.getByRole("button", { name: "Open limits" }));
    expect(screen.getByRole("dialog", { name: "Limits and misuse notice" })).toHaveTextContent("Not an official warning.");
  });

  it("closes on Escape and returns focus to the opener", () => {
    render(<Harness />);
    const opener = screen.getByRole("button", { name: "Open limits" });
    opener.focus();
    fireEvent.click(opener);
    const dialog = screen.getByRole("dialog", { name: "Limits and misuse notice" });
    fireEvent(dialog, new Event("cancel", { cancelable: true }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(opener).toHaveFocus();
  });

  it("closes with the Done button", () => {
    render(<Harness />);
    fireEvent.click(screen.getByRole("button", { name: "Open limits" }));
    fireEvent.click(screen.getByRole("button", { name: "Done" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
