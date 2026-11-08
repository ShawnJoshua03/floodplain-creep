# Design reference

Phone screenshots chosen by the human, 2026-11-07. DESIGN_RULES.md still wins if they disagree.

## Follow

- `apple-maps-sheet.png`: a floating sheet with inset margins and rounded corners over a full-bleed map. A grabber sits at the top. The sheet is a blurred material. A large title, a rounded search field, then plain rows with hairline separators.
- `apple-findmy-sheet.png`: the same sheet holding a "Devices" list. Name and detail on the left, one value on the right (distance). Round icon at the left of each row. Floating round controls on the map edge.
- `apple-weather-rows.png`: one grouped block of rows with hairline separators. Label on the left, a range bar on the right. A segmented control with icons sits in the block header.
- `apple-music-scrubber.png`: the scrubber. A thick rounded track, elapsed and remaining time under it, large plain play controls.

## Avoid

- `avoid-climatecentral-map.png` and `avoid-climatecentral-cards.png`: a dense legend box, many control strips, a stack of cards with colored side borders, a "NEW" badge, and underlined "See all" links. Useful for what the data shows (scenario headline, risk counts). Do not copy the styling. These patterns are banned in DESIGN_RULES.md.
