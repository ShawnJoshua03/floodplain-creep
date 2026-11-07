# Sources

All checked 2026-11-07.

## Open Buildings 2.5D Temporal (Google Research)
- Page: https://sites.research.google/gr/open-buildings/temporal
- Earth Engine collection: `GOOGLE/Research/open-buildings-temporal/v1`.
- Used path: public GCS bucket `open-buildings-temporal-data`, read over HTTPS with no account.
  - Manifests: `v1/manifests/<hash>_EPSG_<code>_<year>_06_30.json`. Several manifests per UTM zone and year.
  - Tile URL: manifest `uriPrefix` joined directly (no slash) to the tile `uris[0]`, with `gs://` mapped to `https://storage.googleapis.com/`.
  - Example: `https://storage.googleapis.com/open-buildings-temporal-data/v1/geotiffs/18dcc_2016_06_30/tile_i2tlsJFt5Oo.tif`.
- Source tiles: 3 float32 bands, 25000 x 25000 px at 0.5 m, tiled 512 x 512, deflate, nodata -99, UTM CRS (Nairobi is EPSG:32737). Tiles are 12.5 km squares aligned to 4 m.
- Bands: `building_fractional_count`, `building_height`, `building_presence`.
- License: CC BY-4.0 and ODbL v1.0 (dual).
- Page notes: effective resolution about 4 m. Presence confidence is uncalibrated. Use height only where presence is high.
- Page does not give a counting method or a presence threshold (it points to the technical report). We have not read the report. Settle this in M2 before using counts.
- Our derived rasters: `data/raw/buildings/buildings_<year>.tif`, 4 m pixels (8 x 8 source pixels), EPSG:32737, nodata -99.
  - count is the sum of fractional counts (totals are preserved). Height and presence are the block maximum.
  - Box 249900..264944 E, 9850280..9865228 N, 3737 x 3761 px.

## JRC Global River Flood Hazard Maps v2.1.2 (Copernicus EMS)
- Folder: https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/ and its `README.txt`.
- 3 arc seconds (~90 m), EPSG:4326, depth in metres, return periods 10, 20, 50, 75, 100, 200, 500.
- Tiles are 10 degrees; `tile_extents.geojson` gives ids. Nairobi is `ID151_N0_E30` (30..40 E, -10..0 N).
- Names: `RP<rp>/ID151_N0_E30_RP<rp>_depth.tif`, `Permanent_WaterBodies/ID151_N0_E30_permanent_water.tif`, `Spurious_Depths/ID151_N0_E30_spurious_depth_areas.tif`.
- Rasters: 11999 x 11999 px, float32, nodata -9999 (depth). Permanent water and spurious depth: nodata 255.
- License: Open Data Commons Open Database License v1.0.
- README warns of unrealistic depths near tile edges and in DEM artefacts. Spurious depth marks depths over 10 m in small channels (under 3,000 km2) for RP10, plus a 2 km buffer.
- Finding for the current box: no modeled river flooding in central Nairobi. See DECISIONS.md.

## Neighborhood boundaries
Not chosen yet. Needed in M2.
