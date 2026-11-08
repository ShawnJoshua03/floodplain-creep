# DESIGN_RULES.md

Goal: the app should feel like a native Apple-platform app. Calm, clear, and content first.
The map is the hero. The interface stays out of its way.

This is a visual language, not a copy of Apple's assets. Do not use Apple logos, icons,
trademarks, or font files. Apple's license does not allow self-hosting its SF fonts on a
website. Use the system font stack, so Apple devices show SF and other devices show their own
interface font. The app will look slightly different on each platform. That is expected.

Tie-breaker for every choice: pick the quieter option. Remove before you add.

## 0. Principles

1. Clarity. One purpose per view. Plain words. Every number has a label and a unit.
2. Deference. The data comes first. Controls are quiet and float above the content.
3. Depth. Layers show hierarchy: map, then sheet, then dialog. Blur and one shadow express
   depth. Nothing is decorative.

## 1. How these rules are enforced

- `scripts/check_design_rules.py`, run by `make design-check` and `make check`. It has tests in
  `tests/test_design_rules.py`. You may add checks. Never weaken one.
- A contrast test over `web/src/styles/tokens.css`.
- The design review gate in section 9. A human looks at screenshots.
- No new dependencies for design. No UI kit, no icon library, no animation library, no web
  fonts. Plain CSS Modules plus the token file.

If a check blocks you, fix the design. Do not work around the check.

## 2. Banned "AI look" patterns

| Pattern | Do this instead |
|---|---|
| Gradients of any kind, including gradient text and shimmer skeletons | Flat semantic colors. Static placeholder rows with a small activity indicator |
| Glow, neon, or colored shadows. Shadows on every card | One floating shadow token for the sheet. Hairline separators elsewhere |
| Colored left-border cards or callouts | Grouped list rows, or plain text in footnote style |
| Emoji, sparkle icons, icons inside colored circles | A small internal line-icon set drawn at text weight |
| Purple, pink, or neon accents | One accent, system blue, used only for things you can press or select |
| Bento grids and walls of equal cards | One map, one sheet, one list |
| Cards inside cards | One grouped list per section |
| Pill badges and chips as decoration ("AI", "Beta", "Verified") | A footnote line in secondary text |
| Rows of big stat tiles | Rows in a grouped list: label on the left, value on the right |
| All-caps, wide-tracked micro labels | Sentence case at footnote size |
| Centered hero with two buttons | None. The map is the first thing people see |
| Glass on content areas | Blur only on floating chrome (sheet, scrubber, dialog) |
| Bouncing, pulsing, floating, or looping animation | Short fades and slides, started by the user |
| Marketing words ("powered by AI", "seamless", "magic", "unlock") | Say what it does in plain words |
| Oversized radii and heavy borders | Radii of 10, 14, and 20 px. One-pixel hairlines |
| Decorative illustrations, stock images, background patterns | Nothing |

## 3. Tokens (one source of truth)

`web/src/styles/tokens.css` defines every color, size, radius, duration, easing, shadow, and
font. Nothing else defines them. Components use `var(--token)` only.

- Mode: dark only (human decision, 2026-11-07). `color-scheme: dark`. No light values and no mode switch.
- Roles: `--bg`, `--bg-grouped`, `--bg-row`, `--label`, `--label-secondary`,
  `--label-tertiary`, `--separator`, `--accent`, `--accent-contrast`, `--fill-nodata`,
  `--chrome-bg` (the translucent color behind blur).
- Data colors: `--ramp-exposure-1` to `--ramp-exposure-5` (one hue) and `--ramp-depth-1` to
  `--ramp-depth-4` (one blue hue). Each step differs in lightness, so the ramp works without
  color vision. The ramps run from dim to bright, so more exposure is more visible.
  No red and green pairs. The accent is never a data color.
- Contrast: text 4.5 to 1 or better, and icons and control boundaries 3 to 1 or better, in
  dark mode. The contrast test covers the listed pairs. Starting values to tune:
  `--bg #000000`, `--bg-grouped #0A0A0C`, `--bg-row #1C1C1E`, `--accent #0A84FF`. Secondary
  labels must be lighter than the usual iOS defaults to pass 4.5 to 1.
- Type: system stack only (`system-ui` first). Two weights only, 400 and 600. Scale:
  `--text-large-title` 2.125rem, `--text-title` 1.75rem, `--text-headline` 1.0625rem at 600,
  `--text-body` 1.0625rem, `--text-subhead` 0.9375rem, `--text-footnote` 0.8125rem,
  `--text-caption` 0.75rem, each with a line-height token. Numbers use tabular figures.
  Sentence case everywhere. No manual letter-spacing, except one token for the large title.
- Space: 4 px base. `--space-1` (0.25rem) through `--space-10` (2.5rem). `--hit-target` 2.75rem.
- Radii: `--radius-control` 0.625rem, `--radius-group` 0.875rem, `--radius-sheet` 1.25rem. An inner
  radius equals the outer radius minus the padding between them.
- Shadow: one token, `--shadow-floating`, used only by the sheet, the scrubber, and the dialog.
- Focus: `--focus-ring` (2 px solid accent) and an offset of `--space-1`.
- Motion: `--duration-fast` 150ms, `--duration-base` 250ms, `--duration-slow` 350ms, and one
  `--ease-standard`. Animate only opacity, transform, and color.

## 4. Layout

- The map fills the viewport edge to edge. There is no page header and no frame around it.
- One floating sheet holds all controls and data.
  - Desktop only. The sheet sits at the left, inset by `--space-3`, `--sheet-width` wide,
    with its own scroll. It uses the chrome material and `--radius-sheet`.
  - There is no phone or tablet layout. Design for 1280 px wide and up.
- Inside the sheet, navigation is a stack: a root view, then detail views, each with a large
  title and a back button labeled with the previous title. Views slide at `--duration-base`.
  Focus moves to the new title after each push or pop.
- The year scrubber floats at the bottom center of the map.
- One info button at the top right of the map opens the Limits dialog.
- Everything is left aligned. Center only empty states.
- Group sections are separated by `--space-6`. Rows are at least `--hit-target` tall.
- At most three type sizes per view, not counting the large title.

## 5. Components (the only ones)

Sheet, NavStack, LargeTitle, SegmentedControl (native radio inputs), GroupedList and Row (label
left, value right, optional chevron), SwitchRow (native checkbox with the switch role),
Scrubber (native range input plus a play button), Dialog (native `dialog` element),
InlineMessage (loading, error, empty), Icon (play, pause, chevron, info, check, close).

- At most one filled button per view. Other actions are plain text buttons.
- No toasts, no popovers, no tooltips except the map name label, and no modals other than the
  Limits dialog.
- Icons are inline SVG components in `web/src/components/icons/`. Stroke width matches the text
  weight. Colors come from classes, not from attributes.

## 6. Map styling

- No basemap tiles. The background is `--bg-grouped`.
- Neighborhoods use the exposure ramp with one-pixel `--separator` outlines. The selected one
  gets a two-pixel `--accent` outline. Suppressed ones use `--fill-nodata` with a dashed outline.
- The depth overlay is an image drawn with the depth ramp at about 70 percent opacity.
- No text layers on the map, because they need a glyph source. Names show in a small material
  label on hover or selection, and in the list.
- Map colors are read from the CSS variables at runtime, and refreshed when the color scheme
  changes. No color is written twice.

## 7. Copy

Sentence case. Short. No exclamation marks, no emoji, no marketing words. Say "Written from the
numbers above," not "AI insights." Every number has a label and a unit. Nothing ships with
placeholder text.

## 8. Accessibility

- Everything works with the keyboard. The focus ring is a 2 px accent outline with an offset,
  shown on `:focus-visible`. It is never removed.
- Targets are at least `--hit-target`.
- Respect reduced motion (durations drop to zero, and the time-lapse never starts by itself),
  reduced transparency (chrome becomes solid), and increased contrast (stronger separators).
- Text scales to 200 percent with no loss. Use rem units and no fixed heights on text.
- Use native elements and real labels. Announce year and scenario changes politely, for
  example "2019, 100-year flood, [N] exposed buildings".
- The map has a text summary, and the ranked list is its accessible alternative.
- Dark mode only. It is designed on purpose, not derived from a light theme.

## 9. Design review gate

Claude Code prepares the screenshots. The human decides. Run at the end of M6 and again at M8.

1. Capture 1440 by 900, in dark mode: root view, neighborhood detail,
   accuracy detail, the Limits dialog, and the loading, error, and not-enough-data states.
   Save them in `docs/design-review/`. Use browser tools, not a new dependency.
2. Squint test. Is the hierarchy still clear when blurred?
3. Grayscale test. Does it still read without color?
4. Remove-one test. Take one element out of each view. If nothing is lost, delete it.
5. Alignment. Do left edges in the sheet line up on one line?
6. Keyboard. Tab through every control and operate it.
7. Pattern scan. Check every row of the section 2 table. Any hit fails the gate.
8. Run `make check`.

Record the result and any changes in `docs/DESIGN_REVIEW.md`.
