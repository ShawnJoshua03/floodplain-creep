# Design review

Gate M6f, run 2026-11-07 against the real API and the Dhaka data. The human decides. Screenshots are in `docs/design-review/`.

## Screenshots taken

- `desktop-root.jpg`: root view with the map.
- `desktop-neighborhood.jpg`: neighborhood detail with the selection outline.
- `desktop-depth-overlay.jpg`: flood depth on, with the depth key and the 1.7 m person.
- `desktop-accuracy.jpg`: accuracy detail.
- `desktop-limits-dialog.jpg`: the Limits dialog.

The browser tool could not change the page viewport, so the viewport was about 1568 by 750, not 1440 by 900.

## Not done yet

- Phone captures at 390 by 844. Needs a real device or a browser with device emulation.
- Screenshots of the loading, error, and not-enough-data states. Each is covered by a test.
- Squint and grayscale tests. A human looks at the screenshots.
- A keyboard pass by a person.
- 200 percent zoom check, increased contrast and reduced transparency checks in a browser.

## Pattern scan (section 2 of DESIGN_RULES.md)

The design checker passes. A visual read of the screenshots found no gradients, glow, colored side borders, emoji, cards inside cards, stat tiles, chips, or marketing words.

## Found by running the app, and fixed

- The map library's worker did not load under Vite, so the map never drew. It now gets the built worker file.
- Feature state was set before the style finished loading, which threw. It now waits for the map to be idle.
- Depth over the amber choropleth turned muddy grey. The choropleth now dims to 35 percent opacity while the depth layer is on.
- The depth overlay prop changed identity on every render, which reloaded the image on every mouse move and froze the page. It is now memoized.

## Open points for the human

- The central neighborhoods are all "not enough data" at the 100-year scenario, so the middle of the map is the no-data gray. That is the K rule working, but it is the first thing people see.
- The accuracy card shows AI-label results. They are unaudited. Do not publish them before the audit.
- The dashed outline for suppressed neighborhoods is hard to see at this size.
