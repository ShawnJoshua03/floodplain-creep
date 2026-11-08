import type { FocusView } from "../api/types";
import { focusView } from "../testing/fixtures";
import { balanceSentence, otherNeighborhoodsNote, ratioText, takeawaySentence } from "./verdict";

function withSignal(verdict: FocusView["signal"]["verdict"], times: number | null, view = focusView(10)): FocusView {
  return { ...view, signal: { ...view.signal, verdict, times_typical_swing: times } };
}

describe("verdict", () => {
  it("words the balance as gaining areas for each losing area", () => {
    expect(ratioText(595, 141)).toBe("4.2 to 1");
    expect(ratioText(10, 0)).toBeNull();
  });

  it("states clear growth with its size, the year it starts, and how many times the usual swing", () => {
    const text = takeawaySentence(withSignal("clear_growth", 6.38));
    expect(text).toBe("Buildings in Badda's 10-year flood zone grew 16% since 2018. That is 6.4 times the usual yearly swing.");
  });

  it("states a decline as a fall", () => {
    const view = withSignal("clear_decline", 3);
    expect(takeawaySentence(view)).toContain("fell");
  });

  it("says a change within noise is not clearly real, with its sign", () => {
    const text = takeawaySentence(withSignal("within_noise", 1.5));
    expect(text).toContain("changed by +16% since 2018");
    expect(text).toContain("not clearly real");
  });

  it("says when there is not enough data", () => {
    expect(takeawaySentence(withSignal("not_enough_data", null))).toBe(
      "There is not enough data to judge the change in Badda's 10-year flood zone.",
    );
  });

  it("compares the areas here with the rest of the city", () => {
    const text = balanceSentence("Badda", focusView(10).balance);
    expect(text).toContain("by 4.2 to 1 in Badda, against 1.4 to 1 in the rest of the city");
    expect(text).toContain("gained 5 or more buildings");
  });

  it("has no balance sentence without a balance", () => {
    expect(balanceSentence("Badda", null)).toBeNull();
  });

  it("says other neighborhoods also gained, without naming them", () => {
    expect(otherNeighborhoodsNote("Badda")).toBe(
      "Other neighborhoods also gained buildings. Badda is shown because it is the largest case.",
    );
  });
});
