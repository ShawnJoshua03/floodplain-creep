import { type GeoJSONSource, type ImageSource, type LayerSpecification, Map as MapLibreMap, Marker, ScaleControl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";
import { boundsOf } from "../../lib/geometryBounds";
import styles from "./MapView.module.css";
import {
  baseStyle,
  contextLayers,
  FOCUS_SOURCE,
  GROWTH_LAYER,
  GROWTH_SOURCE,
  growthLayer,
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
  tag: string;
  geometry: MapGeometry | null;
  water: MapGeometry | null;
  overlay: OverlayImage | null;
  growth: OverlayImage | null;
}

const SHEET_PADDING_PX = 420;
const EDGE_PADDING_PX = 48;
const BOTTOM_PADDING_PX = 120;
const EMPTY = { type: "FeatureCollection", features: [] } as const;

function fitPadding() {
  return {
    top: EDGE_PADDING_PX,
    right: EDGE_PADDING_PX,
    bottom: EDGE_PADDING_PX + BOTTOM_PADDING_PX,
    left: SHEET_PADDING_PX,
  };
}

interface ImageLayerSpec {
  source: string;
  layer: string;
  make: () => LayerSpecification;
}

/** Shows an image on the map, swaps it in place when the url changes, and removes the layer when it is null. */
function syncImage(map: MapLibreMap, spec: ImageLayerSpec, image: OverlayImage | null) {
  if (!image) {
    if (map.getLayer(spec.layer)) {
      map.removeLayer(spec.layer);
    }
    return;
  }
  const coordinates = imageCoordinates(image.bounds);
  const existing = map.getSource<ImageSource>(spec.source);
  if (existing) {
    existing.updateImage({ url: image.url, coordinates });
  } else {
    map.addSource(spec.source, { type: "image", url: image.url, coordinates });
  }
  if (!map.getLayer(spec.layer)) {
    map.addLayer(spec.make(), OUTLINE_LAYER);
  }
}

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
export function MapView({ label, tag, geometry, water, overlay, growth }: MapViewProps) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const fitted = useRef(false);
  const fittedToOverlay = useRef(false);
  const tagText = useRef(tag);
  const tagElement = useRef<HTMLDivElement | null>(null);
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
      map.fitBounds(box, { duration: 0, padding: fitPadding() });
    }
    const element = document.createElement("div");
    element.className = `${styles.nameLabel} chrome`;
    element.textContent = tagText.current;
    tagElement.current = element;
    const marker = new Marker({ element }).setLngLat([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]).addTo(map);
    return () => {
      tagElement.current = null;
      marker.remove();
    };
  }, [geometry, ready]);

  useEffect(() => {
    tagText.current = tag;
    if (tagElement.current) {
      tagElement.current.textContent = tag;
    }
  }, [tag]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) {
      return;
    }
    if (overlay && !fittedToOverlay.current) {
      fittedToOverlay.current = true;
      const [west = 0, south = 0, east = 0, north = 0] = overlay.bounds;
      map.fitBounds([west, south, east, north], { duration: 0, padding: fitPadding() });
    }
    syncImage(map, { source: OVERLAY_SOURCE, layer: OVERLAY_LAYER, make: overlayLayer }, overlay);
  }, [overlay, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (map && ready) {
      syncImage(map, { source: GROWTH_SOURCE, layer: GROWTH_LAYER, make: growthLayer }, growth);
    }
  }, [growth, ready]);

  return <div ref={container} className={styles.map} role="img" aria-label={label} />;
}
