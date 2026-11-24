<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE study protocol

**Status: FROZEN v1.0 (owner-approved 2026-11-24).** The owner approved the freeze with amendments on 2026-11-24 and ruled on the tuning grids in a second round the same day ("Approve all"). Every approved amendment is applied below (see "Amendments before freeze"). The SHA-256 hashes of this file, of the three experiment protocols and of the confirmatory configs are recorded in `research/freeze.json` and `research/experiment_registry.csv`. Any later change to a frozen file is a new study or a dated, labelled deviation (G-FREEZE). No confirmatory run has been executed under this protocol.

Experiment-level protocols: `research/experiments/EXP-001/protocol.md`, `EXP-002/protocol.md`, `EXP-003/protocol.md`. Feasibility audit: `research/feasibility.md`.

## 1. Research question

Master prompt question: "How do demand and inventory policies affect prices and availability in a simulated market?"

Operational question (RQ1): In a simulated market for a perishable stock of identical units (for example seats or rooms) sold over a finite booking horizon to heterogeneous, myopic buyers under demand shocks, do a simple occupancy (booking-curve) pricing rule or a simple demand-responsive pricing rule change expected revenue per selling season relative to the best single fixed price, when all three policy families receive the same tuning budget and face identical demand streams?

Secondary questions:
- RQ2: How do the policies differ in sell-through, availability, price volatility and a consumer surplus proxy?
- RQ3: How do the differences depend on price elasticity and on demand-to-capacity tightness (EXP-002)?
- RQ4: Does the primary comparison survive misspecification of the demand model used for tuning (EXP-003)? This is the sensitivity analysis that could invalidate the main interpretation.

## 2. Why revenue is the single primary metric

The master prompt lists revenue, sell-through, a consumer surplus proxy, price volatility and availability. Revenue is chosen as the single primary metric because (a) it is the objective all three policy families are tuned to maximise, so a comparison on it is a fair test of each family on its own terms; (b) the verified literature makes a specific, testable prediction about it: Gallego and van Ryzin (1994) prove that simple fixed-price policies are asymptotically optimal for expected revenue as the volume of expected sales grows, so whether simple dynamic rules beat a well-tuned fixed price at moderate scale is a genuinely open empirical question in this model; (c) the other outcomes are either mechanically determined by the policy class (price volatility is zero for a fixed price by construction) or are proxies whose meaning depends on synthetic valuations (consumer surplus). They are reported in full as secondary metrics and never promoted to primary after seeing results.

## 3. Formal model (summary; full specification in EXP-001)

- Periods t = 1, ..., T (base T = 60). Simulation periods, not calendar days of any real product.
- Initial stock C units (base C = 100); stock x_t, with x_1 = C. Unsold units at the end of period T perish with zero salvage value.
- Two buyer segments s in {L, H} ("early, lower-valuation" and "late, higher-valuation"); shares w_L = 0.7, w_H = 0.3.
- Expected total arrivals over the horizon A = kappa * C (base kappa = 2.0). Segment arrival profiles over time are linear, each normalised to sum to one: a_L(t) proportional to T + 1 - t (decreasing) and a_H(t) proportional to t (increasing). The EXP-003 reversed cell swaps them.
- Demand shocks: a stream-level multiplier M ~ LogNormal(-sigma_M^2 / 2, sigma_M), sigma_M = 0.25, plus surge episodes (each period starts a 3-period surge with probability 0.05; intensity multiplied by 1.8 during a surge). Overlapping surges do not compound: a period inside one or more surges has factor 1.8.
- Arrivals N_{s,t} ~ Poisson(M * A * w_s * a_s(t) * surge_t). Valuations v ~ LogNormal(ln m_s, sigma_v), m_L = 100, m_H = 200 (currency units are abstract), base sigma_v = 0.5.
- Within a period, the arrival order of L and H buyers is a uniform random permutation, fixed in the stream.
- Buyers are myopic and have unit demand: a buyer arriving in period t buys one unit if v >= p_t and x > 0, otherwise leaves for good.
- Policies observe t, x_t and past prices and sales only (not valuations, not arrivals of non-buyers).
- Price bounds [p_min, p_max] = [30, 600].

Because buyers are myopic, the demand stream (arrival times, order and valuations) does not depend on the policy. Each stream is therefore pre-generated once and replayed identically under every policy (common random numbers), which makes policy comparisons exactly paired.

## 4. Policies

- **FIX(p)** (baseline, primary comparator): p_t = p for all t.
- **OCC(p0, k)**: booking-curve occupancy rule. With f_t = (C - x_t) / C the fraction sold and e_t = (t - 1) / T the fraction of the horizon elapsed, p_t = clip(p0 * exp(k * (f_t - e_t)), p_min, p_max). k = 0 reduces to FIX(p0).
- **DRP(p0, eta)**: demand-responsive rule. p_1 = p0. After each period, r_hat is an exponentially weighted average of units sold per period (weight 0.3, initialised at C / T); the target rate is r*_t = x_t / (T - t + 1), where x_t is the stock at the start of period t (the literal reading, pinned; the alternative post-period reading x_{t+1} / (T - t) is not used). Then p_{t+1} = clip(p_t * ((r_hat + 0.5) / (r*_t + 0.5))^eta, p_min, p_max). eta = 0 reduces to FIX(p0).

**Fair tuning.** Each family gets the same budget: 36 configurations, each evaluated on the same 500 tuning streams, selected by highest mean revenue (ties: lowest configuration index). FIX: 36 geometrically spaced prices from 40 to 400. OCC: 6 geometrically spaced p0 from 40 to 400 times k in {0.25, 0.5, 1, 2, 4, 8}. DRP: the same 6 p0 times eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1.0}. The widened sensitivity grids stay within the equal budget of 36 configurations per family (6 x 6). Tuning streams and evaluation streams are disjoint by construction; nothing is ever tuned on evaluation streams.

**Grid-edge optima are reported as findings.** For every tuned configuration in every cell, the result records whether it lies on a grid edge (p0 or the FIX price at 40 or 400; k at 0.25 or 8; eta at 0.025 or 1.0). An optimum on an edge is reported as a finding, in the experiment report and in the manuscript, together with the cell, the family and the selected values. It is not a failure, it is not excluded, and the grid is never extended or re-centred after the freeze. Interpretation is fixed in advance: (a) DRP at the lower edge eta = 0.025 means the tuning prefers the least responsive rule offered, that is, a rule close to the nesting point eta = 0, where DRP reduces to the fixed price FIX(p0); a DRP responsiveness of 0 is the fixed price, so such a cell is reported as evidence that the demand-responsive rule adds little or nothing over a fixed price there, and Delta_DRP is read as the value of a nearly fixed price at p0* against FIX*; (b) OCC at the lower edge k = 0.25 is read in the same way (k = 0 is FIX(p0)); (c) an optimum at an upper sensitivity edge (k = 8 or eta = 1.0) or at a p0 edge means a stronger response or a more extreme starting price might earn more, so Delta_j measures the family as gridded and may understate what the family could reach on a wider grid; this is stated as a limitation of that cell. The pre-freeze tuning-only check (J-0006, `results/exploratory/grid_interior_check.json`) found 7 of 20 pilot optima on an edge of this grid, all in EXP-002 cells; this is disclosed, and the confirmatory edge flags are reported whatever they turn out to be.

## 5. Hypotheses (primary, EXP-001)

For j in {OCC, DRP}, let Delta_j = E[R(j*, S) - R(FIX*, S)], the expected paired revenue difference per evaluation stream S, where j* and FIX* are the tuned policies.

- H0_j: Delta_j = 0.
- H1_j: Delta_j != 0 (nondirectional).

Planning expectation (not a hypothesis): based on Gallego and van Ryzin (1994), any gain over a well-tuned fixed price is expected to be small at this scale; the study is designed to estimate it precisely, not to demonstrate a gain.

Decision rule: H0_j is rejected when the Bonferroni-adjusted 97.5% paired bootstrap percentile interval for Delta_j excludes zero (family-wise alpha = 0.05 over the two contrasts). Smallest effect size of interest (SESOI): 1% of mean FIX* revenue. Results are classified as: detectable and practically relevant (interval excludes 0 and the point estimate exceeds the SESOI in magnitude); detectable but below SESOI; practically equivalent (interval inside +/- SESOI); inconclusive (interval includes 0 and extends beyond the SESOI). Non-rejection is never reported as equivalence unless the equivalence criterion holds.

What would contradict H1_j: an interval that includes zero. What would contradict the planning expectation: a gain larger than 5% of FIX* revenue.

## 6. Secondary metrics (all per evaluation stream, reported with the same paired bootstrap at 95%, no multiplicity adjustment, labelled descriptive)

- Sell-through: units sold / C (dimensionless, 0 to 1).
- Availability: share of arriving buyers who found x > 0 (defined as 1 when there are no arrivals); also the stock-out period (first t with x = 0, or T + 1).
- Price volatility: (1 / (T - 1)) * sum_t |ln p_t - ln p_{t-1}| (per period, dimensionless). Zero for FIX by construction; reported, not tested against FIX.
- Consumer surplus proxy: sum over buyers of (v_i - p_paid) (currency units). Proxy only: valuations are synthetic.
- Total surplus proxy: revenue + consumer surplus proxy (no costs modelled).
- Mean price paid, overall and by segment.

## 7. Units, seeds and sample size

- Experimental unit: one evaluation demand stream within one scenario cell. The three policies are within-unit treatments; observations are paired by stream.
- Seeds: numpy `SeedSequence(entropy=20261124, spawn_key=(experiment, cell, role, index))`; role 0 (tune) or 1 (eval); tuning indices 0 to 499, evaluation indices 0 to 3999. Every stochastic arm therefore has 4,000 independent evaluation seeds per cell.
- Sample-size rationale: n = 4,000 evaluation streams per cell (owner-approved amendment, 2026-11-24). The exploratory pilot on tuning streams only (journal J-0003 to J-0005, `results/exploratory/pilot_summary.json`) estimated the SD of the paired revenue differences. With the normal approximation at two-sided alpha = 0.025 and power 0.89, the 1% SESOI needs n = 384 (OCC) and 680 (DRP) at the base cell, at most 2,735 across the EXP-002 cells and at most 3,435 across the EXP-003 cells; n = 4,000 covers every pilot cell. These pilot estimates rest on 50 streams and are planning inputs, not evidence. n is fixed at the freeze and never changed after it.
- Uncertainty method: stream-level paired percentile bootstrap, 10,000 resamples, fixed bootstrap seed; paired t interval reported as a cross-check; per-stream raw distributions are exported and plotted.

## 8. Exclusion and stopping rules

- No stream is excluded for its outcome. A run that raises an error or violates an invariant (stock conservation, non-negative stock, price within bounds, no sale when sold out, no sale below price) is recorded as a failure with its traceback in the run manifest.
- Any invariant violation in a confirmatory run stops the experiment. It is treated as an implementation defect: fixed under M2 tests, then the whole matrix is rerun from scratch with a dated deviation note. Partial matrices are never interpreted.
- Fixed sample size, single analysis, no interim looks, no optional stopping.

## 9. Matrices

- **Smoke matrix (exploratory, tuning streams only):** base cell; FIX, OCC, DRP at one hand-set configuration each; 5 seeds; plus edge cases (zero demand, C = 1, all valuations below p_min, demand far above capacity). Purpose: validate invariants and metric code, measure runtime. Never interpreted as evidence.
- **Full matrix (confirmatory once frozen):**
  - EXP-001: base cell, 3 policies plus the tuning-grid sensitivity arm (FIX6), 4,000 evaluation streams (73,000 runs: 57,000 tuning, 16,000 evaluation).
  - EXP-002: sigma_v in {0.25, 0.5, 1.0} times kappa in {1.0, 2.0, 4.0}: 9 cells, each re-tuned, 4,000 evaluation streams per cell (594,000 runs).
  - EXP-003: policies tuned at the base cell, evaluated without re-tuning on 6 misspecified cells (demand level times 0.6, 0.8, 1.25, 1.6; reversed segment arrival order; no shocks), with a re-tuned FIX reference per cell, 4,000 evaluation streams per cell (258,000 runs, including the 54,000 runs that re-derive the base tuning from the EXP-001 tuning-stream keys).
  - Run counts are those printed by `fare.cli run --plan` for the frozen confirmatory configs.
- Compute budget: at most one CPU-hour of wall-clock for all confirmatory runs on the audited laptop; runtime and peak memory are recorded per experiment.

## 10. Sensitivity analyses that could invalidate the main interpretation

1. **Misspecification (EXP-003).** If the sign of Delta_j at the base cell reverses under a moderate demand-level shift (times 0.8 or times 1.25), any advantage found in EXP-001 is declared specific to a correctly specified tuning distribution, and the manuscript must say so.
2. **Tuning-grid sensitivity (inside EXP-001).** FIX gets 36 distinct prices while OCC and DRP get only 6 distinct starting prices. FIX is re-tuned on the same 6-price grid (arm FIX6); if Delta_j changes sign or class, the result is attributed to grid resolution rather than to policy structure.
3. **Elasticity and tightness (EXP-002).** A result that holds in only one cell is reported as cell-specific.

## 11. Confounders and controls

- Demand streams are identical across policies (common random numbers), so stream-level variance is removed from contrasts.
- The tuning budget is equal across families; tuning and evaluation streams are disjoint.
- The nesting property (k = 0 or eta = 0 gives FIX) is tested in M2 so that implementation differences between families cannot masquerade as policy effects.
- Known confound: myopic buyers. Strategic waiting (Su, 2007) is out of scope; results do not extend to strategic buyers.

## 12. Out of scope (owner decision, 2026-11-24)

- No dynamic-programming reference policy (known-model optimum) is computed or reported.
- The optional scale-sensitivity experiment (varying C with proportional demand) is not run and has no EXP ID.

## 13. Implementation choices pinned in this protocol (from decision D-006)

- Project entropy 20261124; spawn-key layout (experiment, cell, role, index).
- Linear arrival profiles, uniform random within-period arrival order and non-compounding surges (section 3).
- DRP target rate with the stock at the start of period t (section 4).
- EXP-003 re-derives the base tuning from the EXP-001 tuning-stream keys (experiment 1, cell 0) instead of reading an EXP-001 result file; the tuned configurations are identical by construction.
- Exploratory configs may not use evaluation streams (role 1).
- The simulator is the bisection simulator in `src/fare/simulate.py`, checked against the naive buyer-by-buyer oracle by differential tests.

## 14. Claims boundary

All results are simulated and hold only within this model. No airline or hotel personalisation claims, no live scraping, no prediction of actual fares, no inference about any proprietary pricing system, and no causal claims about human behaviour.

## Amendments before freeze (owner-approved 2026-11-24)

The owner approved the following on 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24.md`, FARE section; proposals in decision D-007). Applied in draft v0.2 on 2026-11-24 (decision D-008).

1. **Stream counts.** 4,000 evaluation streams and 500 tuning streams per cell (sections 4, 7 and 9; all three EXP protocols and configs). Applied.
2. **Tuning grids.** "Widen the OCC and DRP tuning grids so the pilot optima are interior." **Not applied in the first round: it could not be applied as written; resolved in the second round below.** The proposed grid (6 p0 values times OCC k in {0.25, 0.5, 1, 2, 4, 8} and DRP eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1}) was checked by tuning only, on the pilot tuning streams 0 to 49, without any evaluation (`experiments/exploratory/grid_interior_check.py`, `results/exploratory/grid_interior_check.json`, journal J-0006). It makes the base-cell optima interior (EXP-001, and the EXP-003 base tuning), but 7 of the 20 pilot optima stay on a grid edge, all in EXP-002 cells: OCC at k = 8 in two cells and at k = 0.25 in one, DRP at eta = 0.025 in four. A further tuning-only probe found the DRP optimum at eta = 0 (DRP reduced to a fixed price) in two kappa = 1.0 cells, so no widening of a positive eta grid can make those optima interior. The draft grid of section 4 was therefore kept, and the item went back to the owner (decision D-008).
3. **Scope.** No dynamic-programming reference policy; the optional scale experiment is out of scope (section 12). Applied.
4. **Pinned implementation choices** of D-006 and the DRP target reading (sections 3, 4 and 13). Applied.
5. **EXP-002 interaction contrasts.** Named method: independent stratified percentile bootstrap (EXP-002 protocol section 5). Applied and implemented (`fare.stats.interaction_bootstrap_ci`, report table).
6. **Command names.** The reproduction commands in the EXP protocols now name the implemented CLI. Applied.

## Amendments before freeze, second round (owner-approved 2026-11-24)

On 2026-11-24 the owner answered "Approve all" to the coordinator's recommendations (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24b.md`, section 2): "Keep the widened grids within the equal tuning budget. Report optima on a grid edge as a finding (a DRP responsiveness of 0 means the dynamic rule reduces to a fixed price). Freeze." Applied on 2026-11-24, before any confirmatory data (decision D-009).

7. **Tuning grids.** The widened grids replace the draft grid: 6 p0 values times OCC k in {0.25, 0.5, 1, 2, 4, 8} and DRP eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1.0}, 36 configurations per family, FIX unchanged at 36 prices (section 4). The tuning-grid sensitivity arm becomes FIX6 (section 10). The EXP-001 run count becomes 73,000 (section 9); EXP-002 and EXP-003 are unchanged. Applied.
8. **Grid-edge reporting rule.** Optima on a grid edge are reported as findings, with the interpretation fixed in section 4. Applied.
9. **Freeze.** This protocol, the three experiment protocols and the three confirmatory configs are frozen as v1.0 (`research/freeze.json`). Applied.
