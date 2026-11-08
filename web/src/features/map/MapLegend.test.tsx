import { render, screen } from "@testing-library/react";
import { MapLegend } from "./MapLegend";

const bins = [{ min_depth_m: 0.1, max_depth_m: 0.5, color: "var(--ramp-depth-1)" }];

describe("MapLegend", () => {
  it("is a named region that explains the depth colors and the water", () => {
    render(<MapLegend bins={bins} />);
    expect(screen.getByRole("complementary", { name: "Map legend" })).toBeInTheDocument();
    expect(screen.getByText("0.1 to 0.5 m")).toBeInTheDocument();
    expect(screen.getByText("River or lake, water all year")).toBeInTheDocument();
  });

  it("keeps the person for scale and the modeled-and-approximate note", () => {
    render(<MapLegend bins={bins} />);
    expect(screen.getByText("1.7 m")).toBeInTheDocument();
    expect(screen.getByText(/Modeled and approximate/)).toBeInTheDocument();
  });
});
