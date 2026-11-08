import { createContext, type ReactNode, useContext, useMemo, useReducer } from "react";

interface Selection {
  year: number;
  returnPeriod: number;
  overlayOn: boolean;
  /** The scenarios the city supports. Read once from the API and never changed. */
  returnPeriods: number[];
  /** The one neighborhood the app shows, and its city. Read once from the API and never changed. */
  focusName: string;
  city: string;
}

type Action =
  | { type: "setYear"; year: number }
  | { type: "setReturnPeriod"; returnPeriod: number }
  | { type: "setOverlay"; overlayOn: boolean };

interface SelectionApi extends Selection {
  setYear: (year: number) => void;
  setReturnPeriod: (returnPeriod: number) => void;
  setOverlay: (overlayOn: boolean) => void;
}

function reduce(state: Selection, action: Action): Selection {
  switch (action.type) {
    case "setYear":
      return { ...state, year: action.year };
    case "setReturnPeriod":
      return { ...state, returnPeriod: action.returnPeriod };
    case "setOverlay":
      return { ...state, overlayOn: action.overlayOn };
  }
}

const SelectionContext = createContext<SelectionApi | null>(null);

interface ProviderProps {
  initial: Selection;
  children: ReactNode;
}

export function SelectionProvider({ initial, children }: ProviderProps) {
  const [state, dispatch] = useReducer(reduce, initial);
  const value = useMemo<SelectionApi>(
    () => ({
      ...state,
      setYear: (year) => dispatch({ type: "setYear", year }),
      setReturnPeriod: (returnPeriod) => dispatch({ type: "setReturnPeriod", returnPeriod }),
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
