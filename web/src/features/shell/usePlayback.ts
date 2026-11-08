import { useEffect, useState } from "react";
import { nextYear, PLAY_STEP_MS } from "../../lib/playback";

interface Playback {
  playing: boolean;
  toggle: () => void;
}

/**
 * Steps the year forward while playing and stops at the last year. It never starts by itself.
 * Pressing play on the last year starts again from the first.
 */
export function usePlayback(
  year: number,
  firstYear: number,
  lastYear: number,
  setYear: (year: number) => void,
): Playback {
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    if (!playing) {
      return undefined;
    }
    const timer = window.setTimeout(() => {
      const next = nextYear(year, lastYear);
      if (next === null) {
        setPlaying(false);
      } else {
        setYear(next);
      }
    }, PLAY_STEP_MS);
    return () => window.clearTimeout(timer);
  }, [playing, year, lastYear, setYear]);

  function toggle() {
    if (!playing && year >= lastYear) {
      setYear(firstYear);
    }
    setPlaying(!playing);
  }

  return { playing, toggle };
}
