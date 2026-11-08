import { type GeoJSONSource, type ImageSource, Map as MapLibreMap, Marker, ScaleControl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";
import { boundsOf } from "../../lib/geometryBounds";
import styles from "./MapView.module.css";
import {
  baseStyle,
  contextLayers,
  FOCUS_SOURCE,
  OUTLINE_LAYER,
  OVERLAY_LAYER,
  OVERLAY_SOURCE,
  overlayLayer,
  WATER_SOURCE,
} from "./mapStyle";
import { configureMapWorker } from "./mapWorker";
import { readPalette } from "./readPalette";

interface MapGeometry {
  type: "Polygon" | "MultiPolygon";
  coordinates: number[][][] | number[][][][];
}

interface OverlayImage {
  url: string;
  bounds: number[];
}

interface MapViewProps {
  label: string;
  name: string;
  geometry: MapGeometry | null;
  water: MapGeometry | null;
  overlay: OverlayImage | null;
}

const DESKTOP_MIN_WIDTH = 900;
const SHEET_PADDING_PX = 420;
const EDGE_PADDING_PX = 48;
const BOTTOM_PADDING_PX = 120;
const EMPTY = { type: "FeatureCollection", features: [] } as const;

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
export function MapView({ label, name, geometry, water, overlay }: MapViewProps) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const fitted = useRef(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!container.current) {
      return undefined;
    }
    configureMapWorker();
    const colors = readPalette();
    const map = new MapLibreMap({
      container: container.current,
      style: baseStyle(colors),
      center: [0, 0],
      zoom: 1,
      attributionControl: false,
      dragRotate: false,
      pitchWithRotate: false,
    });
    mapRef.current = map;
    map.addControl(new ScaleControl({ unit: "metric" }), "bottom-right");
    map.on("load", () => {
      map.addSource(WATER_SOURCE, { type: "geojson", data: EMPTY });
      map.addSource(FOCUS_SOURCE, { type: "geojson", data: EMPTY });
      for (const layer of contextLayers(colors)) {
        map.addLayer(layer);
      }
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
    const source = ready ? map?.getSource<GeoJSONSource>(WATER_SOURCE) : undefined;
    if (source) {
      source.setData(water ? { type: "Feature", properties: {}, geometry: water } : EMPTY);
    }
  }, [water, ready]);

  useEffect(() => {
    const map = mapRef.current;
    const source = ready ? map?.getSource<GeoJSONSource>(FOCUS_SOURCE) : undefined;
    if (!map || !source || !geometry) {
      return undefined;
    }
    source.setData({ type: "Feature", properties: {}, geometry });
    const box = boundsOf([geometry]);
    if (!box) {
      return undefined;
    }
    if (!fitted.current) {
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
    const element = document.createElement("div");
    element.className = `${styles.nameLabel} chrome`;
    element.textContent = name;
    const marker = new Marker({ element }).setLngLat([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]).addTo(map);
    return () => {
      marker.remove();
    };
  }, [geometry, name, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) {
      return;
    }
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
      map.addLayer(overlayLayer(), OUTLINE_LAYER);
    }
  }, [overlay, ready]);

  return <div ref={container} className={styles.map} role="img" aria-label={label} />;
}
