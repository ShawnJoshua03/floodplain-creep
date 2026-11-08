import { createContext, type ReactNode, useContext, useMemo, useReducer } from "react";

interface Selection {
  year: number;
  returnPeriod: number;
  neighborhoodId: string | null;
  overlayOn: boolean;
}

type Action =
  | { type: "setYear"; year: number }
  | { type: "setReturnPeriod"; returnPeriod: number }
  | { type: "selectNeighborhood"; neighborhoodId: string | null }
  | { type: "setOverlay"; overlayOn: boolean };

interface SelectionApi extends Selection {
  setYear: (year: number) => void;
  setReturnPeriod: (returnPeriod: number) => void;
  selectNeighborhood: (neighborhoodId: string | null) => void;
  setOverlay: (overlayOn: boolean) => void;
}

function reduce(state: Selection, action: Action): Selection {
  switch (action.type) {
    case "setYear":
      return { ...state, year: action.year };
    case "setReturnPeriod":
      return { ...state, returnPeriod: action.returnPeriod };
    case "selectNeighborhood":
      return { ...state, neighborhoodId: action.neighborhoodId };
    case "setOverlay":
      return { ...state, overlayOn: action.overlayOn };
  }
}

const SelectionContext = createContext<SelectionApi | null>(null);

interface ProviderProps {
  initial: Pick<Selection, "year" | "returnPeriod">;
  children: ReactNode;
}

export function SelectionProvider({ initial, children }: ProviderProps) {
  const [state, dispatch] = useReducer(reduce, { ...initial, neighborhoodId: null, overlayOn: false });
  const value = useMemo<SelectionApi>(
    () => ({
      ...state,
      setYear: (year) => dispatch({ type: "setYear", year }),
      setReturnPeriod: (returnPeriod) => dispatch({ type: "setReturnPeriod", returnPeriod }),
      selectNeighborhood: (neighborhoodId) => dispatch({ type: "selectNeighborhood", neighborhoodId }),
      setOverlay: (overlayOn) => dispatch({ type: "setOverlay", overlayOn }),
    }),
    [state],
  );
  return <SelectionContext.Provider value={value}>{children}</SelectionContext.Provider>;
}

export function useSelection(): SelectionApi {
  const value = useContext(SelectionContext);
  if (!value) {
    throw new Error("useSelection must be used inside SelectionProvider.");
  }
  return value;
}
