import { render, screen } from "@testing-library/react";
import { MapLegend } from "./MapLegend";

const bins = [{ min_depth_m: 0.1, max_depth_m: 0.5, color: "var(--ramp-depth-1)" }];

describe("MapLegend", () => {
  it("is a named region that explains the depth colors and the water", () => {
    render(<MapLegend depthBins={bins} growth={null} />);
    expect(screen.getByRole("complementary", { name: "Map legend" })).toBeInTheDocument();
    expect(screen.getByText("0.1 to 0.5 m")).toBeInTheDocument();
    expect(screen.getByText("River or lake, water all year")).toBeInTheDocument();
  });

  it("keeps the person for scale and the modeled-and-approximate note", () => {
    render(<MapLegend depthBins={bins} growth={null} />);
    expect(screen.getByText("1.7 m")).toBeInTheDocument();
    expect(screen.getByText(/Modeled and approximate/)).toBeInTheDocument();
  });
});

describe("MapLegend growth key", () => {
  it("explains the building density colors and the hidden blocks", () => {
    const growth = { bins: [{ min_buildings: 20, max_buildings: null, color: "var(--ramp-growth-1)" }], blockMeters: 500 };
    render(<MapLegend depthBins={null} growth={growth} />);
    expect(screen.getByText("20 or more")).toBeInTheDocument();
    expect(screen.getByText(/Per 500 m block/)).toBeInTheDocument();
  });
});
