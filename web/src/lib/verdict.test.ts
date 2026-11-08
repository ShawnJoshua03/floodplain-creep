import type { FocusView } from "../api/types";
import { otherNeighborhoodsNote, ratioText, verdictSentence } from "./verdict";

type Signal = FocusView["signal"];

const balance = {
  threshold_buildings: 5,
  focus: { cells_gaining: 595, cells_losing: 141 },
  rest_of_city: { cells_gaining: 1188, cells_losing: 854 },
};

function signal(verdict: Signal["verdict"], times: number | null): Signal {
  return { verdict, smoothed_change_pct: 9.9, times_typical_swing: times, required_multiple: 2 };
}

describe("verdict", () => {
  it("words the balance as gaining areas for each losing area", () => {
    expect(ratioText(595, 141)).toBe("4.2 to 1");
    expect(ratioText(10, 0)).toBeNull();
  });

  it("says clear growth with its multiple and the balance", () => {
    const text = verdictSentence("Badda", signal("clear_growth", 2.11), balance);
    expect(text).toContain("growth in Badda is 2.1 times the usual swing");
    expect(text).toContain("4.2 to 1");
  });

  it("says a change within noise is below the multiple needed", () => {
    const text = verdictSentence("Badda", signal("within_noise", 1.83), balance);
    expect(text).toContain("1.8 times the usual swing, below the 2 times needed");
  });

  it("says a decline as a decline", () => {
    expect(verdictSentence("Badda", signal("clear_decline", 3), null)).toContain("decline in Badda");
  });

  it("says when there is not enough data", () => {
    expect(verdictSentence("Badda", signal("not_enough_data", null), null)).toContain("not enough data");
  });

  it("says other neighborhoods also gained, without naming them", () => {
    expect(otherNeighborhoodsNote("Badda")).toBe(
      "Other neighborhoods also gained buildings. Badda is shown because it is the largest case.",
    );
  });
});
