import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach } from "vitest";
import { PLAY_STEP_MS } from "../../lib/playback";
import { usePlayback } from "./usePlayback";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("usePlayback", () => {
  it("never starts by itself", () => {
    const setYear = vi.fn();
    renderHook(() => usePlayback(2018, 2023, setYear));
    act(() => vi.advanceTimersByTime(PLAY_STEP_MS * 3));
    expect(setYear).not.toHaveBeenCalled();
  });

  it("steps one year at a time once started", () => {
    const setYear = vi.fn();
    const { result } = renderHook(() => usePlayback(2018, 2023, setYear));
    act(() => result.current.toggle());
    act(() => vi.advanceTimersByTime(PLAY_STEP_MS));
    expect(setYear).toHaveBeenCalledWith(2019);
  });

  it("stops at the last year", () => {
    const setYear = vi.fn();
    const { result, rerender } = renderHook(({ year }) => usePlayback(year, 2023, setYear), {
      initialProps: { year: 2022 },
    });
    act(() => result.current.toggle());
    act(() => vi.advanceTimersByTime(PLAY_STEP_MS));
    expect(setYear).toHaveBeenCalledWith(2023);
    rerender({ year: 2023 });
    act(() => vi.advanceTimersByTime(PLAY_STEP_MS));
    expect(result.current.playing).toBe(false);
  });

  it("does not start from the last year", () => {
    const { result } = renderHook(() => usePlayback(2023, 2023, vi.fn()));
    act(() => result.current.toggle());
    expect(result.current.playing).toBe(false);
  });
});
