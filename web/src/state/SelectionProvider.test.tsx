import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { SelectionProvider, useSelection } from "./SelectionProvider";

function wrapper({ children }: { children: ReactNode }) {
  return <SelectionProvider initial={{ year: 2023, returnPeriod: 100 }}>{children}</SelectionProvider>;
}

describe("SelectionProvider", () => {
  it("starts with the given year and scenario, nothing selected, and the overlay off", () => {
    const { result } = renderHook(() => useSelection(), { wrapper });
    expect(result.current).toMatchObject({ year: 2023, returnPeriod: 100, neighborhoodId: null, overlayOn: false });
  });

  it("updates each field on its own", () => {
    const { result } = renderHook(() => useSelection(), { wrapper });
    act(() => result.current.setYear(2020));
    act(() => result.current.setReturnPeriod(50));
    act(() => result.current.selectNeighborhood("n1"));
    act(() => result.current.setOverlay(true));
    expect(result.current).toMatchObject({ year: 2020, returnPeriod: 50, neighborhoodId: "n1", overlayOn: true });
  });

  it("refuses to be read outside the provider", () => {
    expect(() => renderHook(() => useSelection())).toThrow("inside SelectionProvider");
  });
});
