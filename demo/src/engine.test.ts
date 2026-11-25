// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// The sandbox port against the Python engine. Fixture:
// src/fixtures/engine_fixture.json, written by scripts/make_sandbox_fixture.py.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  BASE_SCENARIO, computeMetrics, EngineError, generateStream, mulberry32, simulate,
  type Arrival, type Policy, type Scenario,
} from "./engine";

interface Run {
  policy: Policy;
  prices: number[];
  sales: number[];
  stock: number[];
  metrics: Record<string, number | null>;
}
interface Case { name: string; scenario: Scenario; T: number; arrivals: Arrival[]; runs: Run[] }
interface Moments { n: number; mean: number; sd: number }
interface Dist { name: string; scenario: Scenario; fix_policy: Policy; arrivals: Moments; fix_revenue: Moments; mean_valuation: Moments }
const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8")) as {
  tolerance_relative: number; distribution_z_max: number; cases: Case[]; distribution: Dist[];
};

const TOL = fx.tolerance_relative;
const close = (a: number, b: number) => Math.abs(a - b) <= TOL * Math.max(1, Math.abs(b));

describe("sandbox simulator equals the Python engine on fixed arrivals (relative tolerance 1e-9)", () => {
  for (const c of fx.cases) {
    it(c.name, () => {
      for (const r of c.runs) {
        const o = simulate({ T: c.T, arrivals: c.arrivals }, c.scenario, r.policy);
        expect(o.sales).toEqual(r.sales);
        expect(o.stock).toEqual(r.stock);
        o.prices.forEach((p, t) => expect(close(p, r.prices[t]), `${r.policy.family} price t=${t + 1}`).toBe(true));
        const m = computeMetrics(o, c.scenario) as unknown as Record<string, number | null>;
        for (const [k, v] of Object.entries(r.metrics)) {
          if (v === null) expect(m[k]).toBeNull();
          else expect(close(m[k] as number, v), `${r.policy.family} ${k}: ${m[k]} vs ${v}`).toBe(true);
        }
      }
    });
  }
});

describe("sandbox demand generator matches the Python generator in distribution", () => {
  for (const d of fx.distribution) {
    it(`${d.name}: arrivals, FIX revenue and mean valuation within ${fx.distribution_z_max} standard errors`, () => {
      const u = mulberry32(20261125);
      const arr: number[] = [], rev: number[] = [], val: number[] = [];
      const n = d.arrivals.n;
      for (let i = 0; i < n; i++) {
        const s = generateStream(d.scenario, u);
        arr.push(s.arrivals.length);
        rev.push(simulate(s, d.scenario, d.fix_policy).revenue);
        if (s.arrivals.length) val.push(s.arrivals.reduce((a, x) => a + x[2], 0) / s.arrivals.length);
      }
      const mom = (xs: number[]) => {
        const mu = xs.reduce((a, b) => a + b, 0) / xs.length;
        const sd = Math.sqrt(xs.reduce((a, b) => a + (b - mu) ** 2, 0) / (xs.length - 1));
        return { n: xs.length, mean: mu, sd };
      };
      for (const [js, py] of [[mom(arr), d.arrivals], [mom(rev), d.fix_revenue], [mom(val), d.mean_valuation]] as const) {
        const se = Math.sqrt(js.sd ** 2 / js.n + py.sd ** 2 / py.n);
        expect(Math.abs(js.mean - py.mean) / se).toBeLessThan(fx.distribution_z_max);
      }
    });
  }
});

describe("sandbox engine edge cases", () => {
  it("nesting: k = 0 and eta = 0 reproduce FIX(p0)", () => {
    const s = generateStream(BASE_SCENARIO, mulberry32(7));
    const fix = simulate(s, BASE_SCENARIO, { family: "FIX", params: { p: 133 } });
    expect(simulate(s, BASE_SCENARIO, { family: "OCC", params: { p0: 133, k: 0 } }).prices).toEqual(fix.prices);
    expect(simulate(s, BASE_SCENARIO, { family: "DRP", params: { p0: 133, eta: 0 } }).revenue).toBe(fix.revenue);
  });
  it("rejects invalid policy parameters", () => {
    const s = { T: 60, arrivals: [] };
    expect(() => simulate(s, BASE_SCENARIO, { family: "FIX", params: { p: -1 } })).toThrow(EngineError);
    expect(() => simulate(s, BASE_SCENARIO, { family: "OCC", params: { p0: 100, k: Number.NaN } })).toThrow(EngineError);
  });
  it("is deterministic in the seed", () => {
    expect(generateStream(BASE_SCENARIO, mulberry32(3))).toEqual(generateStream(BASE_SCENARIO, mulberry32(3)));
  });
});
