/** What a return period means, in plain words. */
export function scenarioNote(returnPeriod: number): string {
  return `Ground the model floods about once in ${returnPeriod} years. A simulated scenario, not a forecast.`;
}
