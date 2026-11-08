import { render, screen } from "@testing-library/react";
import { EvidenceChart } from "./EvidenceChart";

const points = [
  { year: 2018, count: 1000 },
  { year: 2019, count: 1100 },
  { year: 2020, count: null },
  { year: 2021, count: 1300 },
];

describe("EvidenceChart", () => {
  it("describes every year in words, including a year with not enough data", () => {
    render(<EvidenceChart points={points} band={{ center: 1000, swingPct: 5 }} selectedYear={2019} caption="Caption" />);
    const label = screen.getByRole("img").getAttribute("aria-label") ?? "";
    expect(label).toContain("2018 1,000");
    expect(label).toContain("2020 not enough data");
    expect(label).toContain("shaded band");
  });

  it("marks the selected year and draws one dot per shown year", () => {
    const { container } = render(
      <EvidenceChart points={points} band={null} selectedYear={2019} caption="Caption" />,
    );
    expect(container.querySelectorAll("circle")).toHaveLength(3);
  });

  it("shows its caption", () => {
    render(<EvidenceChart points={points} band={null} selectedYear={2019} caption="Shaded band is the swing." />);
    expect(screen.getByText("Shaded band is the swing.")).toBeInTheDocument();
  });
});
