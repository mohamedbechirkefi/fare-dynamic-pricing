<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE study protocol

**Status: DRAFT v0.1 (2026-11-24). Not frozen. Awaiting owner review and freeze (G-FREEZE).** No confirmatory run may be executed or evaluated under this protocol until the owner has frozen it and its SHA-256 hash is recorded in `research/experiment_registry.csv` and `research/decision_log.md`. All numeric parameter values below are planning proposals, open to change before the freeze.

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
- Expected total arrivals over the horizon A = kappa * C (base kappa = 2.0). Segment arrival profiles over time: L decreasing, H increasing, each normalised to sum to one.
- Demand shocks: a stream-level multiplier M ~ LogNormal(-sigma_M^2 / 2, sigma_M), sigma_M = 0.25, plus surge episodes (each period starts a 3-period surge with probability 0.05; intensity multiplied by 1.8 during a surge).
- Arrivals N_{s,t} ~ Poisson(M * A * w_s * a_s(t) * surge_t). Valuations v ~ LogNormal(ln m_s, sigma_v), m_L = 100, m_H = 200 (currency units are abstract), base sigma_v = 0.5.
- Buyers are myopic and have unit demand: a buyer arriving in period t buys one unit if v >= p_t and x > 0, otherwise leaves for good.
- Policies observe t, x_t and past prices and sales only (not valuations, not arrivals of non-buyers).
- Price bounds [p_min, p_max] = [30, 600].

Because buyers are myopic, the demand stream (arrival times, order and valuations) does not depend on the policy. Each stream is therefore pre-generated once and replayed identically under every policy (common random numbers), which makes policy comparisons exactly paired.

## 4. Policies

- **FIX(p)** (baseline, primary comparator): p_t = p for all t.
- **OCC(p0, k)**: booking-curve occupancy rule. With f_t = (C - x_t) / C the fraction sold and e_t = (t - 1) / T the fraction of the horizon elapsed, p_t = clip(p0 * exp(k * (f_t - e_t)), p_min, p_max). k = 0 reduces to FIX(p0).
- **DRP(p0, eta)**: demand-responsive rule. p_1 = p0. After each period, r_hat is an exponentially weighted average of units sold per period (weight 0.3, initialised at C / T); the target rate is r*_t = x_t / (T - t + 1). Then p_{t+1} = clip(p_t * ((r_hat + 0.5) / (r*_t + 0.5))^eta, p_min, p_max). eta = 0 reduces to FIX(p0).

**Fair tuning.** Each family gets the same budget: 36 configurations, each evaluated on the same 100 tuning streams, selected by highest mean revenue (ties: lowest configuration index). FIX: 36 geometrically spaced prices from 40 to 400. OCC: 9 geometrically spaced p0 from 40 to 400 times k in {0.5, 1, 2, 4}. DRP: the same 9 p0 times eta in {0.1, 0.25, 0.5, 1.0}. Tuning streams and evaluation streams are disjoint by construction; nothing is ever tuned on evaluation streams.

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
- Seeds: numpy `SeedSequence` with spawn keys (experiment, cell, role, index); role in {tune, eval}; tuning indices 0 to 99, evaluation indices 0 to 299. Every stochastic arm therefore has 300 independent evaluation seeds, well above the minimum of five.
- Sample-size rationale: for a two-sided paired test at alpha = 0.025 per contrast, n = 300 gives about 89% power to detect a standardised paired effect d_z = 0.2 (normal approximation: 0.2 * sqrt(300) - 2.24 = 1.22, Phi(1.22) = 0.89). The standard deviation of paired differences is unknown; an exploratory pilot on tuning streams only (never evaluation streams) may estimate it before the freeze, and n may be raised before the freeze, never after.
- Uncertainty method: stream-level paired percentile bootstrap, 10,000 resamples, fixed bootstrap seed; paired t interval reported as a cross-check; per-stream raw distributions are exported and plotted.

## 8. Exclusion and stopping rules

- No stream is excluded for its outcome. A run that raises an error or violates an invariant (stock conservation, non-negative stock, price within bounds, no sale when sold out, no sale below price) is recorded as a failure with its traceback in the run manifest.
- Any invariant violation in a confirmatory run stops the experiment. It is treated as an implementation defect: fixed under M2 tests, then the whole matrix is rerun from scratch with a dated deviation note. Partial matrices are never interpreted.
- Fixed sample size, single analysis, no interim looks, no optional stopping.

## 9. Matrices

- **Smoke matrix (exploratory, tuning streams only):** base cell; FIX, OCC, DRP at one hand-set configuration each; 5 seeds; plus edge cases (zero demand, C = 1, all valuations below p_min, demand far above capacity). Purpose: validate invariants and metric code, measure runtime. Never interpreted as evidence.
- **Full matrix (confirmatory once frozen):**
  - EXP-001: base cell, 3 policies, 300 evaluation streams (900 evaluation runs plus 10,800 tuning runs).
  - EXP-002: sigma_v in {0.25, 0.5, 1.0} times kappa in {1.0, 2.0, 4.0}: 9 cells, each re-tuned, 300 evaluation streams per cell.
  - EXP-003: policies tuned at the base cell, evaluated without re-tuning on 6 misspecified cells (demand level times 0.6, 0.8, 1.25, 1.6; reversed segment arrival order; no shocks), with a re-tuned FIX reference per cell, 300 evaluation streams per cell.
- Compute budget: at most one CPU-hour of wall-clock for all confirmatory runs on the audited laptop; runtime and peak memory are recorded per experiment.

## 10. Sensitivity analyses that could invalidate the main interpretation

1. **Misspecification (EXP-003).** If the sign of Delta_j at the base cell reverses under a moderate demand-level shift (times 0.8 or times 1.25), any advantage found in EXP-001 is declared specific to a correctly specified tuning distribution, and the manuscript must say so.
2. **Tuning-grid sensitivity (inside EXP-001).** FIX gets 36 distinct prices while OCC and DRP get only 9 distinct starting prices. FIX is re-tuned on the same 9-price grid; if Delta_j changes sign or class, the result is attributed to grid resolution rather than to policy structure.
3. **Elasticity and tightness (EXP-002).** A result that holds in only one cell is reported as cell-specific.

## 11. Confounders and controls

- Demand streams are identical across policies (common random numbers), so stream-level variance is removed from contrasts.
- The tuning budget is equal across families; tuning and evaluation streams are disjoint.
- The nesting property (k = 0 or eta = 0 gives FIX) is tested in M2 so that implementation differences between families cannot masquerade as policy effects.
- Known confound: myopic buyers. Strategic waiting (Su, 2007) is out of scope; results do not extend to strategic buyers.

## 12. Claims boundary

All results are simulated and hold only within this model. No airline or hotel personalisation claims, no live scraping, no prediction of actual fares, no inference about any proprietary pricing system, and no causal claims about human behaviour.
