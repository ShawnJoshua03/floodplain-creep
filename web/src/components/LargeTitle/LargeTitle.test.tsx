import { render, screen } from "@testing-library/react";
import { LargeTitle } from "./LargeTitle";

describe("LargeTitle", () => {
  it("renders the title as the page heading with an optional subtitle", () => {
    render(<LargeTitle title="Floodplain Creep" subtitle="Dhaka" />);
    expect(screen.getByRole("heading", { level: 1, name: "Floodplain Creep" })).toBeInTheDocument();
    expect(screen.getByText("Dhaka")).toBeInTheDocument();
  });

  it("omits the subtitle when none is given", () => {
    render(<LargeTitle title="Mirpur" />);
    expect(screen.queryByText("Dhaka")).not.toBeInTheDocument();
  });
});
