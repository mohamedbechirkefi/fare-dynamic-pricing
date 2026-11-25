<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
<!-- Draft for Medium (master prompt section 8). Not published. Every number is copied from research/paper/manuscript.md. Links are placeholders until the owner releases the repository. -->

# When does a changing price beat a fixed one? A preregistered simulation

*Draft. All results come from a simulated market and say nothing about any real seller, airline, hotel or fare.*

Anyone who has booked a seat or a room has watched a price move. Behind that movement sits an old question in operations research: if you must sell a fixed stock before a deadline, after which every unsold unit is worth nothing, should the price move at all?

Theory gives a surprising answer for large markets. Gallego and van Ryzin (1994) showed that a well-chosen fixed price is asymptotically optimal as expected sales grow. So the interesting question is a smaller, practical one: at a moderate scale, what do simple dynamic rules gain or lose against a fixed price that has been tuned with the same care?

## The question and the set-up

FARE asks: how do demand and inventory policies affect prices and availability in a simulated market? The market has 100 units, 60 periods and two buyer segments: budget buyers who tend to arrive early and buyers with higher valuations who tend to arrive late. Demand shocks move the whole season up or down, and short surges come and go.

Three policies compete:

- **FIX**, one fixed price for the whole season;
- **OCC**, an occupancy rule that raises the price when stock sells faster than time passes and lowers it otherwise;
- **DRP**, a demand-responsive rule that nudges the price so that the sales rate would clear the remaining stock by the deadline.

Fairness was the main design concern. Each family was tuned on the same 500 tuning streams with the same budget of 36 configurations, and then evaluated on 4,000 separate streams. Buyers are simulated as myopic, so every policy faces exactly the same buyers, which makes every comparison paired. The protocols of all three experiments were frozen by the owner before any evaluation stream existed. In total 925,000 simulated seasons ran, and none failed.

## What was measured

**At the base scenario the rules win, modestly.** OCC and DRP earn +407.0 (97.5% interval [373.2, 440.2], +3.47%) and +462.1 ([426.0, 498.1], +3.94%) currency units per season more than the tuned fixed price. Both effects exceed the smallest effect size of interest set in advance, 1% of fixed-price revenue.

**The sign is not general.** Across a 3 x 3 grid of valuation dispersion and demand-to-capacity ratio, all 18 contrasts reject the null hypothesis after correction, but 8 of them are negative. The rules lose in every cell where expected arrivals only equal capacity, with DRP down to -11.41%. The preregistered pattern "dynamic rules gain more when capacity is tight" holds descriptively for every dispersion and both rules (interaction contrasts from +611.5 to +1,754.1).

**Misspecification cuts both ways.** When the true demand differs from the forecast used for tuning, the preregistered invalidation rule is not triggered: at moderate shifts the rules still beat the equally misspecified fixed price. Against a fixed price re-tuned to the true demand, however, the rules lose at 0.6 times the forecast (-7.47% and -8.52%), and their relevant gains are confined to demand above the forecast.

*Figure (alt text): A line chart of the posted price in each of 60 periods for the fixed price, the occupancy rule and the demand-responsive rule on one simulated season of the base scenario; the fixed price is a flat line at 139.61 while both rules move up and down around it. Below it, the published revenue differences with their 97.5% intervals. Source: the FARE demo, `docs/demo.png`.*

## Where the gain comes from

An exploratory check, made after the results were seen and not part of the frozen analysis, splits the base-cell gain by how much demand each season received. Most of the average gain arises in high-demand seasons, where the fixed price sells out early and the rules sell the same units at higher prices. Even at the base scenario the rules lose on 36.375% (OCC) and 32.15% (DRP) of seasons. Without demand shocks the gain over a correctly tuned fixed price largely disappears (OCC -1.19%, DRP +0.95%).

So, within this model, the value of these simple rules lies in responding to scarcity and to demand above the forecast, not in changing prices as such.

## Limitations

- Everything is simulated. Buyers are myopic, buy one unit and never compare sellers; strategic buyers who wait for a lower price could change the picture.
- The parameter values are planning choices, not estimates of any real market.
- Only two simple rule families were tested, each on a fixed grid; a known-model optimal policy was not computed.
- Several checks are one-sided or exploratory, and they are labelled as such in the manuscript.

## Reproducibility

The protocols, configurations, frozen hashes, experiment reports, manuscript (a preprint draft, not peer-reviewed) and an offline interactive demo are in the project repository: placeholder, to be added by the owner if and when the repository is released. The demo URL is also a placeholder.

*The study was carried out with an AI research and development assistant (Claude Code) under the author's direction; the assistant is not an author.*
