import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { SelectionProvider, useSelection } from "./SelectionProvider";

const INITIAL = {
  year: 2023,
  returnPeriod: 10,
  overlayOn: true,
  returnPeriods: [10, 50],
  focusName: "Badda",
  city: "Dhaka",
};

function wrapper({ children }: { children: ReactNode }) {
  return <SelectionProvider initial={INITIAL}>{children}</SelectionProvider>;
}

describe("SelectionProvider", () => {
  it("starts with the given values", () => {
    const { result } = renderHook(() => useSelection(), { wrapper });
    expect(result.current).toMatchObject(INITIAL);
  });

  it("updates each field on its own", () => {
    const { result } = renderHook(() => useSelection(), { wrapper });
    act(() => result.current.setYear(2020));
    act(() => result.current.setReturnPeriod(50));
    act(() => result.current.setOverlay(false));
    expect(result.current).toMatchObject({ year: 2020, returnPeriod: 50, overlayOn: false, focusName: "Badda" });
  });

  it("refuses to be read outside the provider", () => {
    expect(() => renderHook(() => useSelection())).toThrow("inside SelectionProvider");
  });
});
