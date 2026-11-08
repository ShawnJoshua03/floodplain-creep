import { render, screen } from "@testing-library/react";
import { EvidenceChart } from "./EvidenceChart";

const points = [
  { year: 2018, count: 1000 },
  { year: 2019, count: 1100 },
  { year: 2020, count: null },
  { year: 2021, count: 1300 },
  { year: 2022, count: 1350 },
];

describe("EvidenceChart", () => {
  it("describes every year in words, including a year with not enough data", () => {
    render(<EvidenceChart points={points} band={{ center: 1000, swingPct: 5 }} selectedYear={2019} caption="Caption" />);
    const label = screen.getByRole("img").getAttribute("aria-label") ?? "";
    expect(label).toContain("2018 1,000");
    expect(label).toContain("2020 not enough data");
    expect(label).toContain("shaded band");
  });

  it("labels the band and the value axis", () => {
    render(<EvidenceChart points={points} band={{ center: 1000, swingPct: 5 }} selectedYear={2022} caption="Caption" />);
    expect(screen.getByText("usual yearly swing")).toBeInTheDocument();
    expect(screen.getByText("1,350")).toBeInTheDocument();
    expect(screen.getByText("950")).toBeInTheDocument();
  });

  it("draws one dot per shown year and leaves out the band label when there is no band", () => {
    const { container } = render(<EvidenceChart points={points} band={null} selectedYear={2019} caption="Caption" />);
    expect(container.querySelectorAll("circle")).toHaveLength(4);
    expect(screen.queryByText("usual yearly swing")).not.toBeInTheDocument();
  });

  it("shows its caption", () => {
    render(<EvidenceChart points={points} band={null} selectedYear={2019} caption="Shaded band is the swing." />);
    expect(screen.getByText("Shaded band is the swing.")).toBeInTheDocument();
  });
});
