// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Bounded, cancellable sandbox runs of the ported engine (engine.ts).
// Everything stays in the browser; nothing is sent or stored.
import { computeMetrics, EngineError, generateStream, mulberry32, simulate, validateScenario } from "./engine";
import { ARMS, MAX_STREAMS, type Arm, type SandboxResult, type WorkerReply, type WorkerRequest } from "./sandboxTypes";

let cancelled = false;

const mean = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length;
const sd = (xs: number[]) => {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  return Math.sqrt(xs.reduce((a, b) => a + (b - m) ** 2, 0) / (xs.length - 1));
};

async function run(m: Extract<WorkerRequest, { type: "run" }>): Promise<SandboxResult | null> {
  validateScenario(m.scenario);
  if (!Number.isInteger(m.n) || m.n < 1 || m.n > MAX_STREAMS) throw new EngineError(`streams must be 1 to ${MAX_STREAMS}`);
  if (!Number.isInteger(m.seed) || m.seed < 1) throw new EngineError("seed must be a positive integer");
  const u = mulberry32(m.seed);
  const rev: Record<Arm, number[]> = { FIX: [], OCC: [], DRP: [] };
  const st: Record<Arm, number[]> = { FIX: [], OCC: [], DRP: [] };
  const av: Record<Arm, number[]> = { FIX: [], OCC: [], DRP: [] };
  const vol: Record<Arm, number[]> = { FIX: [], OCC: [], DRP: [] };
  const first = {} as SandboxResult["first"];
  for (let i = 0; i < m.n; i++) {
    const s = generateStream(m.scenario, u);
    for (const a of ARMS) {
      const o = simulate(s, m.scenario, m.policies[a]);
      const k = computeMetrics(o, m.scenario);
      rev[a].push(k.revenue);
      st[a].push(k.sell_through);
      av[a].push(k.availability);
      vol[a].push(k.price_volatility);
      if (i === 0) first[a] = { prices: o.prices, stock: o.stock };
    }
    if (i % 50 === 49) {
      await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
      if (cancelled) return null;
      postMessage({ type: "progress", fraction: (i + 1) / m.n } satisfies WorkerReply);
    }
  }
  const arms = {} as SandboxResult["arms"];
  for (const a of ARMS) {
    arms[a] = { revenue_mean: mean(rev[a]), revenue_sd: sd(rev[a]), sell_through_mean: mean(st[a]),
                availability_mean: mean(av[a]), volatility_mean: mean(vol[a]) };
  }
  const contrasts = (["OCC", "DRP"] as const).map((a) => {
    const d = rev[a].map((x, i) => x - rev.FIX[i]);
    const md = mean(d);
    const half = m.n > 1 ? 1.96 * sd(d) / Math.sqrt(m.n) : 0;
    return { arm: a, mean: md, lo: md - half, hi: md + half, share_loses: d.filter((x) => x < 0).length / m.n };
  });
  return { seed: m.seed, n: m.n, scenario: m.scenario, policies: m.policies, first, arms, contrasts };
}

onmessage = async (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  cancelled = false;
  try {
    const result = await run(m);
    postMessage((result === null ? { type: "cancelled" } : { type: "done", result }) satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
