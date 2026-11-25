// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Browser port of the FARE engine for the visitor sandbox.
//
// - simulate() and the FIX, OCC and DRP controllers are line-by-line ports of
//   src/fare/simulate.py (simulate_reference) and src/fare/policies.py. They are
//   checked against the Python engine on fixed arrivals (engine.test.ts,
//   relative tolerance 1e-9, integers exact).
// - generateStream() follows the model of src/fare/streams.py but draws from a
//   different random-number generator (mulberry32, Box-Muller, Knuth Poisson)
//   than numpy, so a sandbox seed never reproduces a research stream. Only its
//   distribution is checked against the Python generator.

export type ArrivalProfile = "linear" | "linear_reversed" | "flat";

export interface Scenario {
  T: number;
  C: number;
  kappa: number;
  demand_scale: number;
  w_L: number;
  m_L: number;
  m_H: number;
  sigma_v: number;
  sigma_M: number;
  surge_prob: number;
  surge_len: number;
  surge_factor: number;
  arrival_profile: ArrivalProfile;
  p_min: number;
  p_max: number;
}

export const BASE_SCENARIO: Scenario = {
  T: 60, C: 100, kappa: 2.0, demand_scale: 1.0, w_L: 0.7, m_L: 100.0, m_H: 200.0, sigma_v: 0.5,
  sigma_M: 0.25, surge_prob: 0.05, surge_len: 3, surge_factor: 1.8, arrival_profile: "linear",
  p_min: 30.0, p_max: 600.0,
};

export type Policy =
  | { family: "FIX"; params: { p: number } }
  | { family: "OCC"; params: { p0: number; k: number } }
  | { family: "DRP"; params: { p0: number; eta: number; weight?: number } };

/** A season's arrivals in arrival order: [period (1..T), segment (0 = L, 1 = H), valuation]. */
export type Arrival = [number, number, number];
export interface Stream {
  T: number;
  arrivals: Arrival[];
}

export interface Outcome {
  prices: number[];
  sales: number[];
  stock: number[];
  arrivalsPerPeriod: number[];
  arrivalsWithStock: number;
  revenue: number;
  consumerSurplus: number;
}

export interface Metrics {
  revenue: number;
  units_sold: number;
  sell_through: number;
  availability: number;
  stockout_period: number;
  price_volatility: number;
  consumer_surplus: number;
  mean_price_paid: number | null;
}

export class EngineError extends Error {}

const clip = (p: number, lo: number, hi: number) => (p < lo ? lo : p > hi ? hi : p);

interface Controller {
  price(t: number, x: number): number;
  observe(t: number, xStart: number, sold: number): void;
}

function positive(name: string, v: number) {
  if (!Number.isFinite(v) || v <= 0) throw new EngineError(`${name} must be a finite positive number`);
}
function nonneg(name: string, v: number) {
  if (!Number.isFinite(v) || v < 0) throw new EngineError(`${name} must be a finite non-negative number`);
}

export function controller(pol: Policy, sp: Scenario): Controller {
  if (pol.family === "FIX") {
    positive("p", pol.params.p);
    const p = clip(pol.params.p, sp.p_min, sp.p_max);
    return { price: () => p, observe: () => undefined };
  }
  if (pol.family === "OCC") {
    const { p0, k } = pol.params;
    positive("p0", p0);
    nonneg("k", k);
    return {
      price: (t, x) => {
        const f = sp.C > 0 ? (sp.C - x) / sp.C : 1.0;
        const e = (t - 1) / sp.T;
        return clip(p0 * Math.exp(k * (f - e)), sp.p_min, sp.p_max);
      },
      observe: () => undefined,
    };
  }
  if (pol.family === "DRP") {
    const { p0, eta } = pol.params;
    const w = pol.params.weight ?? 0.3;
    positive("p0", p0);
    nonneg("eta", eta);
    if (!(w > 0 && w <= 1)) throw new EngineError("weight must lie in (0, 1]");
    let p = clip(p0, sp.p_min, sp.p_max);
    let rHat = sp.C / sp.T;
    return {
      price: () => p,
      observe: (t, xStart, sold) => {
        rHat = w * sold + (1.0 - w) * rHat;
        const rStar = xStart / (sp.T - t + 1);
        const ratio = (rHat + 0.5) / (rStar + 0.5);
        p = clip(p * ratio ** eta, sp.p_min, sp.p_max);
      },
    };
  }
  throw new EngineError("unknown policy family");
}

/** Buyer-by-buyer simulation (port of simulate_reference), with the invariant checks of check_invariants. */
export function simulate(stream: Stream, sp: Scenario, pol: Policy): Outcome {
  if (stream.T !== sp.T) throw new EngineError("stream horizon differs from the scenario horizon");
  const ctl = controller(pol, sp);
  const T = sp.T;
  const prices: number[] = [];
  const sales: number[] = [];
  const stock: number[] = [sp.C];
  const arrivalsPerPeriod = new Array<number>(T).fill(0);
  let x = sp.C;
  let found = 0;
  let cs = 0;
  let i = 0;
  const a = stream.arrivals;
  for (let t = 1; t <= T; t++) {
    const p = ctl.price(t, x);
    prices.push(p);
    let s = 0;
    const xStart = x;
    while (i < a.length && a[i][0] === t) {
      arrivalsPerPeriod[t - 1] += 1;
      if (x > 0) {
        found += 1;
        const v = a[i][2];
        if (v >= p) {
          x -= 1;
          s += 1;
          cs += v - p;
        }
      }
      i += 1;
    }
    sales.push(s);
    stock.push(x);
    ctl.observe(t, xStart, s);
  }
  if (i !== a.length) throw new EngineError("arrivals must be sorted by period and lie in 1..T");
  let revenue = 0;
  for (let t = 0; t < T; t++) revenue += prices[t] * sales[t];
  const o = { prices, sales, stock, arrivalsPerPeriod, arrivalsWithStock: found, revenue, consumerSurplus: cs };
  checkInvariants(o, sp, a.length);
  return o;
}

function checkInvariants(o: Outcome, sp: Scenario, nArrivals: number) {
  const fail = (m: string) => {
    throw new EngineError(`invariant violated: ${m}`);
  };
  if (o.stock[0] !== sp.C) fail("x_1 must equal C");
  let sold = 0;
  for (let t = 0; t < sp.T; t++) {
    if (o.stock[t + 1] !== o.stock[t] - o.sales[t]) fail("stock conservation");
    if (o.stock[t + 1] < 0 || o.sales[t] < 0) fail("non-negative stock and sales");
    if (o.sales[t] > o.arrivalsPerPeriod[t]) fail("no more sales than arrivals");
    if (!(o.prices[t] >= sp.p_min && o.prices[t] <= sp.p_max)) fail("price bounds");
    sold += o.sales[t];
  }
  if (sold !== sp.C - o.stock[sp.T]) fail("total stock conservation");
  if (o.arrivalsWithStock < 0 || o.arrivalsWithStock > nArrivals) fail("availability accounting");
  if (o.consumerSurplus < -1e-9) fail("no buyer pays above valuation");
}

export function computeMetrics(o: Outcome, sp: Scenario): Metrics {
  const units = o.sales.reduce((s, v) => s + v, 0);
  const arrivals = o.arrivalsPerPeriod.reduce((s, v) => s + v, 0);
  let vol = 0;
  for (let t = 1; t < o.prices.length; t++) vol += Math.abs(Math.log(o.prices[t]) - Math.log(o.prices[t - 1]));
  let stockout = sp.T + 1;
  for (let t = 1; t < o.stock.length; t++) {
    if (o.stock[t] === 0) {
      stockout = t;
      break;
    }
  }
  return {
    revenue: o.revenue,
    units_sold: units,
    sell_through: sp.C > 0 ? units / sp.C : 0,
    availability: arrivals > 0 ? o.arrivalsWithStock / arrivals : 1.0,
    stockout_period: stockout,
    price_volatility: o.prices.length < 2 ? 0 : vol / (o.prices.length - 1),
    consumer_surplus: o.consumerSurplus,
    mean_price_paid: units > 0 ? o.revenue / units : null,
  };
}

// ---------- Demand streams (same model, different random-number generator) ----------

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(u: () => number): number {
  let u1 = u();
  while (u1 <= 0) u1 = u();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u());
}

function poisson(u: () => number, lam: number): number {
  if (lam <= 0) return 0;
  let n = 0;
  let rest = lam;
  while (rest > 0) {
    const part = Math.min(rest, 30);
    rest -= part;
    const L = Math.exp(-part);
    let k = 0;
    let prod = u();
    while (prod > L) {
      k += 1;
      prod *= u();
    }
    n += k;
  }
  return n;
}

export function arrivalProfiles(T: number, kind: ArrivalProfile): [number[], number[]] {
  const t = Array.from({ length: T }, (_, i) => i + 1);
  const sInc = t.reduce((s, v) => s + v, 0);
  const inc = t.map((v) => v / sInc);
  const dec = t.map((v) => (T + 1 - v) / sInc);
  if (kind === "linear") return [dec, inc];
  if (kind === "linear_reversed") return [inc, dec];
  const flat = t.map(() => 1 / T);
  return [flat, flat.slice()];
}

export function validateScenario(sp: Scenario): void {
  const ok =
    Number.isInteger(sp.T) && sp.T >= 1 && sp.T <= 365 && Number.isInteger(sp.C) && sp.C >= 0 && sp.C <= 2000 &&
    sp.kappa >= 0 && sp.kappa <= 20 && sp.demand_scale >= 0 && sp.demand_scale <= 5 && sp.w_L >= 0 && sp.w_L <= 1 &&
    sp.m_L > 0 && sp.m_H > 0 && sp.sigma_v >= 0 && sp.sigma_v <= 3 && sp.sigma_M >= 0 && sp.sigma_M <= 2 &&
    sp.surge_prob >= 0 && sp.surge_prob <= 1 && Number.isInteger(sp.surge_len) && sp.surge_len >= 1 &&
    sp.surge_factor > 0 && sp.surge_factor <= 10 && sp.p_min > 0 && sp.p_min <= sp.p_max &&
    ["linear", "linear_reversed", "flat"].includes(sp.arrival_profile);
  const finite = Object.values(sp).every((v) => typeof v === "string" || Number.isFinite(v));
  if (!ok || !finite) throw new EngineError("scenario parameters are outside the sandbox's bounded domain");
}

export function generateStream(sp: Scenario, u: () => number): Stream {
  const sm = sp.sigma_M;
  const M = sm > 0 ? Math.exp(-0.5 * sm * sm + sm * normal(u)) : 1.0;
  const surge = new Array<boolean>(sp.T).fill(false);
  for (let s = 0; s < sp.T; s++) {
    if (u() < sp.surge_prob) for (let j = s; j < Math.min(sp.T, s + sp.surge_len); j++) surge[j] = true;
  }
  const [aL, aH] = arrivalProfiles(sp.T, sp.arrival_profile);
  const A = sp.kappa * sp.demand_scale * sp.C;
  const arrivals: Arrival[] = [];
  for (let t = 0; t < sp.T; t++) {
    const f = surge[t] ? sp.surge_factor : 1.0;
    const nL = poisson(u, M * A * sp.w_L * aL[t] * f);
    const nH = poisson(u, M * A * (1 - sp.w_L) * aH[t] * f);
    const seg: number[] = [...new Array<number>(nL).fill(0), ...new Array<number>(nH).fill(1)];
    for (let i = seg.length - 1; i > 0; i--) {
      const j = Math.floor(u() * (i + 1));
      [seg[i], seg[j]] = [seg[j], seg[i]];
    }
    for (const g of seg) {
      const med = g === 0 ? sp.m_L : sp.m_H;
      arrivals.push([t + 1, g, med * Math.exp(sp.sigma_v * normal(u))]);
    }
  }
  return { T: sp.T, arrivals };
}
