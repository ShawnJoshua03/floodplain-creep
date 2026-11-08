interface Ranked {
  name: string;
  buildings_in_zone: number | null;
  suppressed: boolean;
}

/** Shown neighborhoods by count, highest first, then suppressed neighborhoods by name. */
export function rankNeighborhoods<T extends Ranked>(items: T[]): T[] {
  return [...items].sort((a, b) => {
    if (a.suppressed !== b.suppressed) {
      return a.suppressed ? 1 : -1;
    }
    const byCount = (b.buildings_in_zone ?? 0) - (a.buildings_in_zone ?? 0);
    return byCount !== 0 ? byCount : a.name.localeCompare(b.name);
  });
}
