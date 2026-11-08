# Sources

All checked 2026-11-07. City: Dhaka (see DECISIONS.md).

## Open Buildings 2.5D Temporal (Google Research)
- Page: https://sites.research.google/gr/open-buildings/temporal
- Earth Engine collection: `GOOGLE/Research/open-buildings-temporal/v1`.
- Used path: public GCS bucket `open-buildings-temporal-data`, read over HTTPS with no account.
  - Manifests: `v1/manifests/<hash>_EPSG_<code>_<year>_06_30.json`. Several manifests per UTM zone and year.
  - Tile URL: manifest `uriPrefix` joined directly (no slash) to the tile `uris[0]`, with `gs://` mapped to `https://storage.googleapis.com/`.
  - Example: `https://storage.googleapis.com/open-buildings-temporal-data/v1/geotiffs/18dcc_2016_06_30/tile_i2tlsJFt5Oo.tif`.
- Source tiles: 3 float32 bands, 25000 x 25000 px at 0.5 m, tiled 512 x 512, deflate, nodata -99, UTM CRS (Dhaka is EPSG:32646). Tiles are 12.5 km squares aligned to 4 m.
- Bands: `building_fractional_count`, `building_height`, `building_presence`.
- License: CC BY-4.0 and ODbL v1.0 (dual).
- Page notes: effective resolution about 4 m. Presence confidence is uncalibrated. Use height only where presence is high.
- Page does not give a counting method or a presence threshold (it points to the technical report). We have not read the report. Settle this in M2 before using counts.
- Our derived rasters: `data/raw/buildings/buildings_<year>.tif`, 4 m pixels (8 x 8 source pixels), EPSG:32737, nodata -99.
  - count is the sum of fractional counts (totals are preserved). Height and presence are the block maximum.
  - Dhaka box about 3.7k x 3.5k px at 4 m, EPSG:32646 (lon 90.3425..90.4775, lat 23.6925..23.8275). Grid is 153 x 142 cells of 100 m.

## JRC Global River Flood Hazard Maps v2.1.2 (Copernicus EMS)
- Folder: https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/ and its `README.txt`.
- 3 arc seconds (~90 m), EPSG:4326, depth in metres, return periods 10, 20, 50, 75, 100, 200, 500.
- Tiles are 10 degrees; `tile_extents.geojson` gives ids. Dhaka is `ID200_N30_E90`.
- Names: `RP<rp>/ID200_N30_E90_RP<rp>_depth.tif`, `Permanent_WaterBodies/ID200_N30_E90_permanent_water.tif`, `Spurious_Depths/ID200_N30_E90_spurious_depth_areas.tif`.
- Rasters: about 12000 x 12000 px, float32, nodata -9999 (depth). Permanent water and spurious depth: nodata 255.
- License: Open Data Commons Open Database License v1.0.
- README warns of unrealistic depths near tile edges and in DEM artefacts. Spurious depth marks depths over 10 m in small channels (under 3,000 km2) for RP10, plus a 2 km buffer.
- Dhaka box at RP100: 14,986 valid depth pixels of 26,244, depth 0.1 to 9.4 m. About 57% of the box area is above 0.1 m.

## Neighborhood boundaries
- geoBoundaries Bangladesh ADM3 (thana level), release gbOpen, year represented 2020, 544 units. Metadata: https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM3/
- Download: https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/BGD/ADM3/geoBoundaries-BGD-ADM3.geojson saved as `data/raw/boundaries/adm3.geojson` (125 MB, gitignored).
- License: CC BY 3.0 IGO. Credit geoBoundaries in the README.
- 40 units touch the box. 33 have at least half their area inside it and are kept, clipped to the box. See DECISIONS.md for the dropped ones.
- Ward level was not found as open data. OpenStreetMap has one ward relation in the box (Mirpur 2). Thana level is the smallest unit we can source.

## Gemini API (checked 2026-11-08)
- Used for: plain-language briefs. Nothing else.
- Model list: `GET https://generativelanguage.googleapis.com/v1beta/models` with the `x-goog-api-key` header. On this date `gemini-2.5-flash` returned 404 "no longer available to new users". `gemini-3.5-flash` answered in about one second and is set in `config/brief.yaml`. `gemini-3.8-flash` and `gemini-3.1-flash-lite` returned 504 deadline errors.
- SDK: `google-genai`, `genai.Client(api_key=..., http_options=...)`, `client.models.generate_content(model, contents, config)`. The config sets `temperature`, `max_output_tokens` and `thinking_config`.
- Finding: with default thinking, `gemini-3.5-flash` spent about 1,150 of 1,200 output tokens thinking and returned a cut-off answer (`finish_reason` MAX_TOKENS). `thinking_level` minimal fixes it. `thinking_budget` 0 also stops the cut-off but made the model repeat field names.
- Key format: Google AI Studio keys are now 53 characters and do not start with `AIza`.
