<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# demo/: FARE interactive research page (M5)

A static booking-market lab for the FARE study. It shows, from the published results only:

- the overview and status (preprint draft, not peer-reviewed; all results simulated);
- **price timelines and policy comparisons**: the posted price of each tuned rule in every period of one evaluation season, for each of the 16 evaluated market cells, next to that cell's published revenue differences with their intervals;
- every registered experiment (EXP-001 to EXP-003) with its status, its verdict under the frozen rule, every estimate with its interval and SESOI class, and its claim ids; negative and positive results are drawn the same way;
- the exploratory checks of M4 (J-0012), labelled exploratory;
- the assumptions, the method and the limitations;
- a **sandbox** that runs the simulator in a Web Worker with seed, reset, cancel, scenario and policy controls.

Labels are distinct on the page: Measured (published, frozen experiments), Exploratory (published, post hoc), Assumption (model inputs), Sandbox (computed in the visitor's browser). Nothing on the page describes, predicts or evaluates any real seller, airline, hotel, fare or pricing system.

## Identity and motion

The page has its own brand: a light itinerary carrying split-flap departure boards (plan and review in `DESIGN.md`). The hero board flips the published base-scenario results into place once on load; the EXP-002 board flips when scrolled into view; chart lines wipe in once; the experiment selector's indicator slides. Intermediate flaps are letters and blanks only, so no number outside the data is ever shown. With reduced motion, every element renders in its final state. Brand files (mark, lockups, favicon, Open Graph image) are in `public/brand/`; the Open Graph image is rendered from `tools/og/og.html` with Chrome headless. The departure board is a visual metaphor only.

## Third-party notes

| Component | Version | Licence | Use |
|---|---|---|---|
| Barlow Condensed (Jeremy Tribby), via `@fontsource/barlow-condensed` | 5.3.0 | SIL Open Font License 1.1 | display type and board glyphs, weights 500 and 600, Latin subset, self-hosted |
| Public Sans (USWDS), via `@fontsource/public-sans` | 5.3.0 | SIL Open Font License 1.1 | body text and tables, weights 400 and 600, Latin subset, self-hosted |

## Data

`public/data/results.json` (schema `lab-demo-results` 1.0.0, plus the keys `exploratory_checks`, `price_paths`, `cells` and `display_exceptions`) is written by `scripts/export_demo_data.py` from committed files only. Every display string is the exact text of `research/paper/manuscript.md`, except the listed display exceptions; `tests/test_demo_export.py` checks this and that the committed file equals a fresh export. The price paths are re-simulated from the committed seed keys and tuned policies, and the export fails unless they reproduce the committed `fig-EXP-NNN-<cell>-price.svg` figures byte for byte. The page validates the file and shows no number if any field is missing or malformed.

## Sandbox fidelity

`src/engine.ts` ports the simulator and the FIX, OCC and DRP rules of `src/fare/`. `src/engine.test.ts` compares it with the Python engine on fixed arrivals (fixture `src/fixtures/engine_fixture.json`, written by `scripts/make_sandbox_fixture.py`): prices and metrics agree within a relative tolerance of 1e-9, and sales and stock exactly. Demand streams follow the same model but use a different random-number generator (mulberry32) than numpy, so a sandbox seed never reproduces a research stream; their distribution (arrivals, fixed-price revenue, mean valuation) is checked against 1,000 Python streams per scenario within 4 standard errors. Sandbox output is labelled as such and is never mixed with the published numbers.

## Commands

Node 22 (on the owner's machine, a shared read-only installation outside this repository).

```
cd demo && npm ci && npm run build && npm run preview     # quick start
npm test                                                  # vitest: results validation and engine port
node tools/a11y_check.mjs dist --screenshots <dir>        # offline, keyboard, contrast, 360 px, reduced motion
```

From the repository root, to regenerate the data:

```
PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py
PYTHONPATH=src .venv/bin/python scripts/make_sandbox_fixture.py
```

## Privacy and offline use

No visitor response is collected or stored and no request leaves the page's origin: no analytics, no fonts, scripts or images from a CDN. After the first load the page works without a network. The sandbox's "Download" button saves the visitor's own sandbox output as a local file; nothing is uploaded. 

## Hosting

The built page (`demo/dist`) is hosted at https://fare-dynamic-pricing.kefimohamedbechir.workers.dev as Cloudflare Workers static assets on the free plan, configured by `demo/wrangler.jsonc` (assets only, no Worker script). It is deployed by the coordinator, not by any script of this repository. Every file the page loads is served from that same origin.
