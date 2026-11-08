import { scenarioNote } from "./scenarios";

describe("scenarioNote", () => {
  it("explains the return period and says it is not a forecast", () => {
    expect(scenarioNote(10)).toBe("Ground the model floods about once in 10 years. A simulated scenario, not a forecast.");
  });
});
