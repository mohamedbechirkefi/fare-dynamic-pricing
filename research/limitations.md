<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Limitations (living document, M0 draft 2026-11-24)

No results exist yet. These are limitations known at design time; the list is extended as the study proceeds.

1. **Simulation only.** All data are synthetic. Results hold only within the model's assumptions and are not evidence about any real market, airline, hotel or proprietary pricing system.
2. **Myopic, unit-demand buyers.** Buyers do not wait strategically, do not return, do not compare competitors and buy at most one unit. Strategic behaviour can change optimal price paths and welfare (Su, 2007).
3. **Monopoly, single product, no competition.** No competing sellers, no product differentiation, no network of resources.
4. **Arbitrary parameter values.** Segment shares, valuation medians, shock sizes and horizons are planning choices, not calibrated estimates. EXP-002 and EXP-003 probe sensitivity but cannot cover every plausible market.
5. **Consumer surplus is a proxy.** It depends on synthetic valuations; it is not a welfare measurement of real people.
6. **Simple policy families.** Only three rule families are compared, each with a 36-configuration tuning budget; the optimal dynamic program is not part of the primary comparison.
7. **No costs.** No marginal, holding or salvage values beyond zero salvage at the deadline.
8. **Toolchain.** No TeX distribution: LaTeX output is generated but not compiled locally; PDFs come from the Typst path.
9. **Literature search is targeted, not systematic.** No novelty claim is made.
10. **Tuning grids may bind.** In the exploratory pilot (J-0003 to J-0005), the tuned DRP and OCC sensitivities sat at edges of the draft grid in every cell. The frozen v1.0 grids are wider within the same 36-configuration budget (D-009), but a tuning-only check (J-0006) still left 7 of 20 pilot optima on an edge, all in EXP-002 cells, and a DRP optimum at eta = 0 (a fixed price) in two cells. Edge optima are reported as findings under the rule of `research/protocol.md` section 4; where an optimum sits on an upper or price edge, the contrast measures the family as gridded.
11. **Unspecified design details.** These details are implementation choices (D-006), not empirically grounded: the arrival-profile shape, the within-period arrival order and the DRP target-rate reading.
12. **Results are cell-specific (EXP-002, confirmatory 2026-11-25).** The dynamic rules beat the tuned fixed price at the base cell (EXP-001) but lose to it in every loose-capacity cell (kappa = 1.0) and in sv1.0-k2.0. No claim of a general advantage of dynamic pricing is supported, even within the model.
13. **Grid edges in the confirmatory tuning.** 8 tuned optima in EXP-002 lie on a grid edge: DRP at eta = 0.025 in sv0.25-k1.0, sv0.5-k1.0, sv1.0-k1.0 and sv1.0-k2.0; OCC at k = 0.25 in sv0.5-k1.0 and sv1.0-k1.0; OCC at k = 8 in sv0.25-k2.0; OCC at p0 = 400 and k = 8 in sv1.0-k4.0. Under the frozen rule, lower edges are read as rules close to a fixed price; the upper and price edges mean the OCC contrast in those two cells measures the family as gridded and may understate it. No edge optimum occurred at the base cell (EXP-001, EXP-003 base tuning).
14. **Sign-flip p-values at the permutation floor.** In EXP-002 every raw p-value equals 1/10001, the smallest value 10,000 permutations can give; Holm-adjusted values (0.0018) are therefore bounds, not precise p-values.
15. **Misspecification is one-sided.** Base-tuned dynamic rules lose to the base-tuned fixed price when demand falls to 0.6 times the tuning level (EXP-003, descriptive), and against a fixed price re-tuned to the true demand they lose at x0.6 and, for OCC, at x0.8 and without shocks. The advantage depends on demand not falling far below the tuning forecast.
16. **Shared machine.** Confirmatory timings were measured with two concurrent jobs on a machine shared with other sessions.
