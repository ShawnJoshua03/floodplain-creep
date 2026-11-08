/** Height of an adult shown beside the depth scale, so depth is easy to picture. */
export const PERSON_HEIGHT_M = 1.7;

/** The depth scale runs from 0 m to this height. The deepest bin is drawn up to it. */
export const SCALE_TOP_M = 2.6;

interface BinRange {
  min_depth_m: number;
  max_depth_m: number | null;
}

/** Position of one depth bin on the scale, as shares of the scale height. */
export function binPosition(bin: BinRange): { from: number; to: number } {
  return { from: bin.min_depth_m / SCALE_TOP_M, to: (bin.max_depth_m ?? SCALE_TOP_M) / SCALE_TOP_M };
}

export function binLabel(bin: BinRange): string {
  return bin.max_depth_m === null ? `${bin.min_depth_m} m and deeper` : `${bin.min_depth_m} to ${bin.max_depth_m} m`;
}
