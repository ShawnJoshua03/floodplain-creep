import { render, screen } from "@testing-library/react";
import { DepthKey } from "./DepthKey";

const bins = [
  { min_depth_m: 0.1, max_depth_m: 0.5, color: "var(--ramp-depth-1)" },
  { min_depth_m: 2, max_depth_m: null, color: "var(--ramp-depth-4)" },
];

describe("DepthKey", () => {
  it("lists each depth bin in metres", () => {
    render(<DepthKey bins={bins} />);
    expect(screen.getByText("0.1 to 0.5 m")).toBeInTheDocument();
    expect(screen.getByText("2 m and deeper")).toBeInTheDocument();
  });

  it("shows a person of known height for scale", () => {
    render(<DepthKey bins={bins} />);
    expect(screen.getByText("1.7 m")).toBeInTheDocument();
  });

  it("says the depth is modeled and approximate", () => {
    render(<DepthKey bins={bins} />);
    expect(screen.getByText(/Modeled and approximate/)).toBeInTheDocument();
  });
});
