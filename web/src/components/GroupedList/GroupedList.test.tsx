import { fireEvent, render, screen } from "@testing-library/react";
import { GroupedList, Row } from "./GroupedList";

describe("GroupedList", () => {
  it("renders a titled list with a footnote", () => {
    render(
      <GroupedList title="Neighborhoods" footer="Counts are relative.">
        <Row label="Mirpur" value="1,200" />
      </GroupedList>,
    );
    expect(screen.getByRole("heading", { name: "Neighborhoods" })).toBeInTheDocument();
    expect(screen.getByRole("list")).toBeInTheDocument();
    expect(screen.getByText("Counts are relative.")).toBeInTheDocument();
  });

  it("shows the label and value in a plain row", () => {
    render(
      <GroupedList>
        <Row label="Accuracy" value="55%" />
      </GroupedList>,
    );
    expect(screen.getByText("Accuracy")).toBeInTheDocument();
    expect(screen.getByText("55%")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("makes a pressable row a button named by its label", () => {
    const onPress = vi.fn();
    render(
      <GroupedList>
        <Row label="Mirpur" value="1,200" onPress={onPress} />
      </GroupedList>,
    );
    fireEvent.click(screen.getByRole("button", { name: /Mirpur/ }));
    expect(onPress).toHaveBeenCalledTimes(1);
  });
});
