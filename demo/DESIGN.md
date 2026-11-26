<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE demo: design plan (owner request, 2026-11-26)

## Subject, audience, job

- **Subject.** A seller with a fixed stock of seats that perish at departure: does changing the price over the
  selling season beat one well-tuned fixed price? The vernacular is the airport: departure boards with split-flap
  digits, boarding passes with a torn stub, gate signage, timetables.
- **Audience.** A curious technical reader, an admissions committee skimming for rigour, a researcher checking the
  numbers.
- **Primary job.** Say the question and the answer in one sentence, show the mixed-sign result the way an airport
  shows its departures (a board that flips into place), then let the reader check every number and run the model.

## Palette (light page, dark boards)

| Name | Hex | Role |
|---|---|---|
| Ticket stock | `#EEF2F5` | page background, a cool grey-blue card stock (not cream) |
| Carbon ink | `#14233A` | text, rules, the logo in one colour |
| Board slate | `#1B2633` | split-flap boards and the logo tile (a blue slate, not near-black) |
| Flap face | `#26333F` | one tile on a board |
| Departure amber | `#F2B544` | board headings and the logo split line, used on slate only |
| Gate blue | `#1C5BA6` | links, focus ring, the selected segment |

Policy inks reuse the study's figures: FIX graphite `#475467`, OCC teal `#0E7068`, DRP signal orange `#B8440B`.
On the board, gains print in pale teal `#8EDCCF` and losses in pale orange `#FFAB85`, always with their sign.

## Type

- **Barlow Condensed** (OFL 1.1), weights 500 and 600: the board glyphs, headlines, navigation, stub labels. Its
  DIN and highway-sign lineage reads as transport signage, and it has tabular figures.
- **Public Sans** (OFL 1.1), weights 400 and 600: body text and tables. A plain, open signage-office sans with
  tabular figures, clearly distinct from the condensed display face.

Scale (1.25 minor third on a 17 px body): 13.6, 17, 21, 26.5, 33, 41, 52 px. Body line length 68ch maximum.

## Layout

The page is a printed itinerary that carries one live board. Left-aligned text column, boards and tickets break
out to the full content width.

```
+---------------------------------------------------------------------------+
| [tile F] FARE   Board  Timelines  Results  Checks  Assumptions  Sandbox    |  sticky, compact
+---------------------------------------------------------------------------+
| Question (Barlow Condensed 52)         | +-------- board slate --------+  |
| Answer sentence (Public Sans 21)       | | Rule Market   vs FIX  /season | |
| status line, author line               | | OCC  base     +3.47%  +407.04 | |
|                                        | | DRP  base     +3.94%  +462.08 | |
|                                        | | DRP  sv1.0..  -11.41% -815.0  | |
|                                        | +------------------------------+  |
+---------------------------------------------------------------------------+
| Key result: the 3 x 3 board (dispersion rows x tightness columns),         |
| each tile OCC and DRP, the loose column visibly negative                   |
+---------------------------------------------------------------------------+
| Price timelines: [EXP-001|EXP-002|EXP-003] segmented, cell select, chart    |
+---------------------------------------------------------------------------+
| Results: one boarding pass per experiment                                  |
|  +stub--+:------------------------------------------------------------+    |
|  |EXP   |: verdict, interval rows                                     |    |
|  |001   |:                                                             |    |
|  +------+:------------------------------------------------------------+    |
+---------------------------------------------------------------------------+
| Exploratory checks (dashed passes), Assumptions, Method and limitations    |
| Sandbox: the check-in desk (form, run, flight-strip output)                |
| Footer: links, licence, AI use, font credits                               |
+---------------------------------------------------------------------------+
```

## Motion

- **Hero moment (once, on load).** The departure board flips each character through a few blank and letter flaps
  before landing on the published value, row by row (row stagger 140 ms, column stagger 34 ms, 60 ms per flap,
  strong ease-out). The intermediate flaps are letters and blanks only, never digits, so no number that is not in
  the data ever appears. The board's text is in the DOM from the first frame for screen readers.
- **Answers to actions.** The segmented control's indicator slides (transform, 220 ms); the price chart's lines
  wipe in once when scrolled into view (clip-path, 700 ms); the 3 x 3 board tiles flip in once when scrolled into
  view (stagger 40 ms); the sandbox run button presses (scale 0.97, 120 ms) and its output arrives with
  `@starting-style` (opacity and 8 px rise, 260 ms).
- **Reduced motion.** No flips, wipes or rises: everything renders in its final state.
- Hover effects only under `(hover: hover) and (pointer: fine)`. No `transition: all`.

## The one memorable thing

The split-flap departure board in the hero that clacks the study's real headline numbers into place.

## Review against the tells and the other demos

- First draft used a near-black board with an acid yellow accent across the page. That is tell 2. Revised: the page
  is light ticket stock; slate boards are contained objects; amber appears only on slate.
- First draft put an all-caps tracked label above every section. Removed: section headings are plain sentence-case
  condensed type; caps appear only inside the board glyphs, where the object itself is uppercase.
- First draft numbered the sections 01 to 07. Removed: the page is not a sequence. Stubs carry the real experiment
  ids (EXP-001 to EXP-003) instead.
- Result panels were identical rounded cards. Revised: boarding passes with a perforated stub and notches, square
  corners on the board, 10 px only on passes, so radius follows the object.
- The search tool proposed Swiss minimalism with Outfit and Work Sans and a sky-blue SaaS palette; rejected as
  generic.
- Against the other studies: STREAK (daylight grade book), MEMORY (index cards in pencil), ECHO (record sleeve),
  PULSE (control room), MARKET (1980s ticker tape, the nearest neighbour: tape is a horizontal stream on a dark
  floor; FARE is a static board of flaps on a light itinerary), TOKEN (thermal die shot), SCALE (blueprint).
- The airport imagery is a visual metaphor only: no copy implies anything about real airlines or fares (claims boundary, master prompt section 10).
