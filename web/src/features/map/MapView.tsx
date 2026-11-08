import { type GeoJSONSource, type ImageSource, Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";
import { boundsOf } from "../../lib/geometryBounds";
import styles from "./MapView.module.css";
import {
  baseStyle,
  FILL_LAYER,
  fillColor,
  fillOpacity,
  focusLayers,
  OUTLINE_LAYER,
  OVERLAY_LAYER,
  OVERLAY_SOURCE,
  overlayLayer,
  SOURCE_ID,
} from "./mapStyle";
import { configureMapWorker } from "./mapWorker";
import { type Palette, readPalette } from "./readPalette";

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
  geometry: MapGeometry | null;
  bucket: number;
  overlay: OverlayImage | null;
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
export function MapView({ label, geometry, bucket, overlay }: MapViewProps) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const palette = useRef<Palette | null>(null);
  const fitted = useRef(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!container.current) {
      return undefined;
    }
    configureMapWorker();
    const colors = readPalette();
    palette.current = colors;
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
    map.on("load", () => {
      map.addSource(SOURCE_ID, { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      for (const layer of focusLayers(colors, 0, false)) {
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
    const source = ready ? map?.getSource<GeoJSONSource>(SOURCE_ID) : undefined;
    if (!map || !source || !geometry) {
      return;
    }
    source.setData({ type: "Feature", properties: {}, geometry });
    const box = boundsOf([geometry]);
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
  }, [geometry, ready]);

  const overlayOn = overlay !== null;
  useEffect(() => {
    const map = mapRef.current;
    const colors = palette.current;
    if (!map || !colors || !ready) {
      return;
    }
    map.setPaintProperty(FILL_LAYER, "fill-color", fillColor(colors, bucket));
    map.setPaintProperty(FILL_LAYER, "fill-opacity", fillOpacity(overlayOn));
  }, [bucket, overlayOn, ready]);

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
