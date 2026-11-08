import { type GeoJSONSource, type ImageSource, Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";
import { boundsOf } from "../../lib/geometryBounds";
import { configureMapWorker } from "./mapWorker";
import styles from "./MapView.module.css";
import {
  baseStyle,
  FILL_LAYER,
  FILL_OPACITY,
  FILL_OPACITY_UNDER_OVERLAY,
  ID_PROPERTY,
  neighborhoodLayers,
  OVERLAY_LAYER,
  OVERLAY_SOURCE,
  overlayLayer,
  SELECTED_LAYER,
  SEPARATOR_LAYER,
  selectedFilter,
  SOURCE_ID,
} from "./mapStyle";
import { readPalette } from "./readPalette";

export interface MapGeometry {
  id: string;
  geometry: { type: "Polygon" | "MultiPolygon"; coordinates: number[][][] | number[][][][] };
}

interface OverlayImage {
  url: string;
  bounds: number[];
}

interface MapViewProps {
  label: string;
  geometries: MapGeometry[];
  buckets: Record<string, number>;
  selectedId: string | null;
  overlay: OverlayImage | null;
  onSelect: (id: string | null) => void;
  onHover: (id: string | null) => void;
}

const DESKTOP_MIN_WIDTH = 900;
const SHEET_PADDING_PX = 420;
const EDGE_PADDING_PX = 48;
const BOTTOM_PADDING_PX = 120;

function imageCoordinates(bounds: number[]): [[number, number], [number, number], [number, number], [number, number]] {
  const [west = 0, south = 0, east = 0, north = 0] = bounds;
  return [
    [west, north],
    [east, north],
    [east, south],
    [west, south],
  ];
}

/** The only file that calls the map library. The map is driven from props through a ref. */
export function MapView({ label, geometries, buckets, selectedId, overlay, onSelect, onHover }: MapViewProps) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const handlers = useRef({ onSelect, onHover });
  const fitted = useRef(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    handlers.current = { onSelect, onHover };
  }, [onSelect, onHover]);

  useEffect(() => {
    if (!container.current) {
      return undefined;
    }
    configureMapWorker();
    const palette = readPalette();
    const map = new MapLibreMap({
      container: container.current,
      style: baseStyle(palette),
      center: [0, 0],
      zoom: 1,
      attributionControl: false,
      dragRotate: false,
      pitchWithRotate: false,
    });
    mapRef.current = map;
    map.on("load", () => {
      map.addSource(SOURCE_ID, {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
        promoteId: ID_PROPERTY,
      });
      for (const layer of neighborhoodLayers(palette)) {
        map.addLayer(layer);
      }
      map.on("click", (event) => {
        const hit = map.queryRenderedFeatures(event.point, { layers: [FILL_LAYER] })[0];
        const id = hit?.properties?.[ID_PROPERTY];
        handlers.current.onSelect(typeof id === "string" ? id : null);
      });
      map.on("mousemove", (event) => {
        const hit = map.queryRenderedFeatures(event.point, { layers: [FILL_LAYER] })[0];
        const id = hit?.properties?.[ID_PROPERTY];
        map.getCanvas().style.cursor = hit ? "pointer" : "";
        handlers.current.onHover(typeof id === "string" ? id : null);
      });
      map.on("mouseout", () => handlers.current.onHover(null));
      setReady(true);
    });
    return () => {
      setReady(false);
      mapRef.current = null;
      map.remove();
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const source = ready ? map?.getSource<GeoJSONSource>(SOURCE_ID) : undefined;
    if (!map || !source || geometries.length === 0) {
      return;
    }
    source.setData({
      type: "FeatureCollection",
      features: geometries.map(({ id, geometry }) => ({
        type: "Feature",
        properties: { [ID_PROPERTY]: id },
        geometry,
      })),
    });
    const box = boundsOf(geometries.map(({ geometry }) => geometry));
    if (box && !fitted.current) {
      fitted.current = true;
      const wide = window.innerWidth >= DESKTOP_MIN_WIDTH;
      map.fitBounds(box, {
        duration: 0,
        padding: {
          top: EDGE_PADDING_PX,
          right: EDGE_PADDING_PX,
          bottom: wide ? EDGE_PADDING_PX + BOTTOM_PADDING_PX : SHEET_PADDING_PX,
          left: wide ? SHEET_PADDING_PX : EDGE_PADDING_PX,
        },
      });
    }
  }, [geometries, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) {
      return undefined;
    }
    const apply = () => {
      for (const [id, bucket] of Object.entries(buckets)) {
        map.setFeatureState({ source: SOURCE_ID, id }, { bucket });
      }
    };
    if (map.isStyleLoaded()) {
      apply();
      return undefined;
    }
    map.once("idle", apply);
    return () => {
      map.off("idle", apply);
    };
  }, [buckets, geometries, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (map && ready) {
      map.setFilter(SELECTED_LAYER, selectedFilter(selectedId));
    }
  }, [selectedId, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) {
      return;
    }
    map.setPaintProperty(FILL_LAYER, "fill-opacity", overlay ? FILL_OPACITY_UNDER_OVERLAY : FILL_OPACITY);
    if (!overlay) {
      if (map.getLayer(OVERLAY_LAYER)) {
        map.removeLayer(OVERLAY_LAYER);
      }
      return;
    }
    const coordinates = imageCoordinates(overlay.bounds);
    const existing = map.getSource<ImageSource>(OVERLAY_SOURCE);
    if (existing) {
      existing.updateImage({ url: overlay.url, coordinates });
    } else {
      map.addSource(OVERLAY_SOURCE, { type: "image", url: overlay.url, coordinates });
    }
    if (!map.getLayer(OVERLAY_LAYER)) {
      map.addLayer(overlayLayer(), SEPARATOR_LAYER);
    }
  }, [overlay, ready]);

  return <div ref={container} className={styles.map} role="img" aria-label={label} />;
}
