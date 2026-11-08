export type Bounds = [west: number, south: number, east: number, north: number];

type Position = number[];
type Coordinates = Position | Coordinates[];

function visit(node: Coordinates, bounds: Bounds): void {
  const [x, y] = node;
  if (typeof x === "number" && typeof y === "number") {
    bounds[0] = Math.min(bounds[0], x);
    bounds[1] = Math.min(bounds[1], y);
    bounds[2] = Math.max(bounds[2], x);
    bounds[3] = Math.max(bounds[3], y);
    return;
  }
  for (const child of node) {
    if (Array.isArray(child)) {
      visit(child, bounds);
    }
  }
}

/** The box around a set of polygons, or null when there are none. */
export function boundsOf(geometries: { coordinates: Coordinates }[]): Bounds | null {
  const bounds: Bounds = [Infinity, Infinity, -Infinity, -Infinity];
  for (const geometry of geometries) {
    visit(geometry.coordinates, bounds);
  }
  return Number.isFinite(bounds[0]) ? bounds : null;
}
