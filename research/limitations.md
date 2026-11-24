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
10. **Tuning grids may bind.** In the exploratory pilot (J-0003 to J-0005), the tuned DRP and OCC sensitivities sit at grid edges in every cell. Unless the grids change before the freeze (D-007), the comparison partly reflects the grid choice.
11. **Unspecified design details.** These details are implementation choices (D-006), not empirically grounded: the arrival-profile shape, the within-period arrival order and the DRP target-rate reading.
