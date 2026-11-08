import { setWorkerUrl } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";

/** Vite does not bundle the map library's worker on its own, so it is given the built file. */
export function configureMapWorker(): void {
  setWorkerUrl(workerUrl);
}
