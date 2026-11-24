<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Literature and dataset review (M0, started 2026-11-24)

This is a targeted search, not a systematic review. Status of each source: **opened (full text)** means the full text was retrieved and the cited statement was checked against it; **opened (abstract/record)** means only the publisher or index record with the abstract was read; **unverified** means only search-result metadata was seen. Only "opened" sources may be cited for content, and only for what was actually read.

## 1. Sources

| Key | Reference | Access | Accessed | What was checked |
|---|---|---|---|---|
| GvR1994 | Gallego, G., and van Ryzin, G. (1994). Optimal Dynamic Pricing of Inventories with Stochastic Demand over Finite Horizons. *Management Science* 40(8), 999-1020. DOI 10.1287/mnsc.40.8.999 | opened (full text, 22 pages), author-hosted PDF: https://business.columbia.edu/sites/default/files-efs/pubfiles/3943/vanryzin_optimal_dynamic_pricing.pdf ; SHA-256 of retrieved bytes 3b9cf08f9e6d4fa621216378e5fe9051dac95a45de4961aa81ac6d070ada7fde (not stored in the repository) | 2026-11-24 | Abstract and journal header: intensity-control formulation; monotonicity of optimal price in stock and horizon; closed form for an exponential demand family; deterministic upper bound; "simple, fixed price policies are asymptotically optimal as the volume of expected sales tends to infinity"; extensions (compound Poisson, finite price set, time-varying rates, holding costs, overbooking, cancellations). |
| GvR1997 | Gallego, G., and van Ryzin, G. (1997). A Multiproduct Dynamic Pricing Problem and Its Applications to Network Yield Management. *Operations Research* 45(1), 24-41. DOI 10.1287/opre.45.1.24 | opened (abstract/record): https://econpapers.repec.org/RePEc:inm:oropre:v:45:y:1997:i:1:p:24-41 | 2026-11-24 | Abstract: deterministic upper bound yields heuristics asymptotically optimal as sales volume grows; network yield management application. |
| EK2003 | Elmaghraby, W., and Keskinocak, P. (2003). Dynamic Pricing in the Presence of Inventory Considerations: Research Overview, Current Practices, and Future Directions. *Management Science* 49(10), 1287-1309. DOI 10.1287/mnsc.49.10.1287.17315 | opened (abstract/record): https://econpapers.repec.org/RePEc:inm:ormnsc:v:49:y:2003:i:10:p:1287-1309 | 2026-11-24 | Abstract: review of dynamic (intertemporal) pricing with inventory; airlines, hotels and utilities as industries with short-run fixed, perishable capacity. |
| Su2007 | Su, X. (2007). Intertemporal Pricing with Strategic Customer Behavior. *Management Science* 53(5), 726-741. DOI 10.1287/mnsc.1060.0667 | opened (abstract/record): https://econpapers.repec.org/RePEc:inm:ormnsc:v:53:y:2007:i:5:p:726-741 | 2026-11-24 | Abstract: customers heterogeneous in valuation and patience; markdowns or increasing prices depending on which segment is more patient; effects on revenue, consumer surplus and welfare. Used only to motivate the myopic-buyer limitation. |
| dB2013 | den Boer, A. V. (2013). *Dynamic Pricing and Learning*. Doctoral thesis, Vrije Universiteit Amsterdam. ISBN 978-90-6464-617-1 | opened (front matter only), CWI repository PDF: https://ir.cwi.nl/pub/21460/21460D.pdf ; SHA-256 d2d18c9c54130a3880475e7ad0ff35513208aaf58a7d3bf2f0708cf2fdb501d7 | 2026-11-24 | Title page, institution, defence date (7 February 2013), ISBN. Content not yet read; not citable for content. |
| AAN2019 | Antonio, N., de Almeida, A., and Nunes, L. (2019). Hotel booking demand datasets. *Data in Brief* 22, 41-49. DOI 10.1016/j.dib.2018.11.126 | opened (full article on PubMed Central): https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/ | 2026-11-24 | Article licence CC BY 4.0; two anonymised booking datasets (40,060 and 79,330 bookings, 31 variables, including average daily rate, arrival date, lead time and cancellation flag), supplied as supplementary files; no separate data licence stated on the page. |
| dB2015 | den Boer, A. V. (2015). Dynamic pricing and learning: historical origins, current research, and new directions. *Surveys in Operations Research and Management Science* 20(1), 1-18 | unverified (search-result metadata only) | 2026-11-24 | Not opened. Do not cite for content. |
| TvR2004 | Talluri, K. T., and van Ryzin, G. J. (2004). *The Theory and Practice of Revenue Management* | unverified (search-result mentions only; publisher not confirmed) | 2026-11-24 | Not opened. |
| BC2003 | Bitran, G., and Caldentey, R. (survey of pricing models for revenue management) | unverified: the author-hosted PDF returned HTTP 404 | 2026-11-24 | Not opened; bibliographic details unconfirmed. |

## 2. What is known (from opened sources only)

- Finite-horizon pricing of a fixed perishable stock under price-sensitive stochastic demand is a classical problem with known structure: the optimal price depends on remaining stock and remaining time (GvR1994).
- A deterministic relaxation gives an upper bound on expected revenue, and fixed-price policies built from it are asymptotically optimal as expected sales grow (GvR1994; GvR1997 for the multiproduct network case).
- Strategic customers who time purchases change the optimal price path and the welfare consequences (Su2007). FARE assumes myopic buyers and so cannot speak to this.

## 3. Narrow contribution (provisional; no novelty claim)

FARE does not propose new theory. Its intended contribution is a transparent, preregistered, fully reproducible simulation that (a) compares a fixed price against two simple, model-free rules (occupancy and demand-responsive) under an equal tuning budget and exactly matched demand streams, (b) reports buyer-side outcomes (availability, a consumer surplus proxy, price volatility) alongside revenue, and (c) pre-specifies a misspecification analysis that can overturn the headline comparison. Whether a comparable open, preregistered study exists has not been established; the search so far is too narrow to claim novelty, and the manuscript must not claim it unless a documented search supports it.

## 4. Candidate datasets

| Dataset | Licence | Redistribution | Status |
|---|---|---|---|
| Hotel booking demand (AAN2019 supplementary files) | Article is CC BY 4.0. The data files are distributed as article supplements; whether the CC BY 4.0 licence explicitly covers the supplements was not confirmed on the page read. | Probably permitted with attribution if CC BY 4.0 covers the supplements; **unclear, owner blocker if ever used**. | Not downloaded. Not needed by the draft protocol. Possible later use: plausibility check of lead-time and price ranges only, never as fare prediction. |
| Mirrors of the hotel booking data on third-party platforms (for example Kaggle) | Unverified | Unverified | Excluded: use the primary source if needed. |
| Scraped airline fare datasets | Typically unclear or terms-of-service restricted | No | Excluded by the claims boundary (no scraping, no actual fare predictions). |
| U.S. DOT/BTS airline origin-and-destination survey (DB1B) | Unverified (not opened) | Unverified | Not planned. |
