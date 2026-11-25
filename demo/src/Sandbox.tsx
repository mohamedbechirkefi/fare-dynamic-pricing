// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Visitor sandbox: runs the ported engine in a Web Worker. Its output is
// labelled as sandbox output and never mixed with the published results.
// Nothing the visitor enters is stored or sent anywhere.
import { useEffect, useMemo, useRef, useState } from "react";
import { BASE_SCENARIO, type ArrivalProfile, type Policy, type Scenario } from "./engine";
import type { CellPreset } from "./results";
import { Legend, pathSummary, TimeChart } from "./charts";
import { ARMS, MAX_STREAMS, type Arm, type SandboxResult, type WorkerReply, type WorkerRequest } from "./sandboxTypes";

interface Form {
  preset: string;
  seed: string;
  n: string;
  C: string;
  kappa: string;
  sigma_v: string;
  demand_scale: string;
  arrival_profile: ArrivalProfile;
  shocks: boolean;
  fix_p: string;
  occ_p0: string;
  occ_k: string;
  drp_p0: string;
  drp_eta: string;
}

const NEUTRAL: Omit<Form, "preset"> = {
  seed: "1", n: "200", C: String(BASE_SCENARIO.C), kappa: String(BASE_SCENARIO.kappa), sigma_v: String(BASE_SCENARIO.sigma_v),
  demand_scale: "1", arrival_profile: "linear", shocks: true,
  fix_p: "140", occ_p0: "140", occ_k: "1", drp_p0: "140", drp_eta: "0.1",
};

const r4 = (x: number) => String(Math.round(x * 100) / 100);

function fromPreset(p: CellPreset | undefined): Form {
  if (!p) return { preset: "", ...NEUTRAL };
  const sc = { ...BASE_SCENARIO, ...p.scenario } as Scenario;
  const P = p.policies;
  return {
    preset: `${p.experiment}|${p.cell_id}`, seed: "1", n: "200", C: String(sc.C), kappa: String(sc.kappa),
    sigma_v: String(sc.sigma_v), demand_scale: String(sc.demand_scale), arrival_profile: sc.arrival_profile,
    shocks: sc.sigma_M > 0 || sc.surge_prob > 0,
    fix_p: r4(P.FIX.params.p), occ_p0: r4(P.OCC.params.p0), occ_k: String(P.OCC.params.k),
    drp_p0: r4(P.DRP.params.p0), drp_eta: String(P.DRP.params.eta),
  };
}

type Parsed = { ok: true; seed: number; n: number; scenario: Scenario; policies: Record<Arm, Policy> } | { ok: false; message: string };

function parse(f: Form): Parsed {
  const bad: string[] = [];
  const num = (name: string, v: string, lo: number, hi: number, int = false) => {
    const x = Number(v);
    if (v.trim() === "" || !Number.isFinite(x) || x < lo || x > hi || (int && !Number.isInteger(x))) {
      bad.push(`${name} must be ${int ? "a whole number " : ""}from ${lo} to ${hi}`);
      return lo;
    }
    return x;
  };
  const seed = num("Seed", f.seed, 1, 1_000_000, true);
  const n = num("Streams", f.n, 1, MAX_STREAMS, true);
  const scenario: Scenario = {
    ...BASE_SCENARIO,
    C: num("Capacity", f.C, 10, 500, true),
    kappa: num("Arrivals to capacity", f.kappa, 0.25, 8),
    sigma_v: num("Valuation dispersion", f.sigma_v, 0.05, 1.5),
    demand_scale: num("Demand versus forecast", f.demand_scale, 0.2, 2.5),
    arrival_profile: f.arrival_profile,
    sigma_M: f.shocks ? BASE_SCENARIO.sigma_M : 0,
    surge_prob: f.shocks ? BASE_SCENARIO.surge_prob : 0,
  };
  const policies: Record<Arm, Policy> = {
    FIX: { family: "FIX", params: { p: num("FIX price", f.fix_p, 30, 600) } },
    OCC: { family: "OCC", params: { p0: num("OCC starting price", f.occ_p0, 30, 600), k: num("OCC sensitivity k", f.occ_k, 0, 10) } },
    DRP: { family: "DRP", params: { p0: num("DRP starting price", f.drp_p0, 30, 600), eta: num("DRP step eta", f.drp_eta, 0, 2), weight: 0.3 } },
  };
  return bad.length ? { ok: false, message: bad.join("; ") } : { ok: true, seed, n, scenario, policies };
}

const f0 = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 0 });
const f3 = (x: number) => x.toFixed(3);
const sg = (x: number) => (x >= 0 ? "+" : "") + f0(x);

export function Sandbox({ presets }: { presets: CellPreset[] }) {
  const worker = useRef<Worker | null>(null);
  const initial = useMemo(() => fromPreset(presets[0]), [presets]);
  const [form, setForm] = useState<Form>(initial);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<SandboxResult | null>(null);
  useEffect(() => setForm(initial), [initial]);

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") setProgress(m.fraction);
      if (m.type === "done") {
        setResult(m.result);
        setStatus(`Sandbox output ready: ${m.result.n} simulated seasons, seed ${m.result.seed}.`);
      }
      if (m.type === "error") setStatus(`Sandbox run failed: ${m.message}`);
      if (m.type === "cancelled") setStatus("Sandbox run cancelled.");
      if (m.type !== "progress") setRunning(false);
    };
    worker.current = w;
    return () => w.terminate();
  }, []);

  const set = <K extends keyof Form>(k: K, v: Form[K]) => setForm((f) => ({ ...f, [k]: v }));
  const choosePreset = (key: string) => {
    const p = presets.find((x) => `${x.experiment}|${x.cell_id}` === key);
    setForm(p ? fromPreset(p) : { preset: "", ...NEUTRAL });
  };
  const run = () => {
    const p = parse(form);
    setStatus("");
    if (!p.ok) {
      setStatus(`Settings outside the sandbox bounds: ${p.message}.`);
      return;
    }
    setRunning(true);
    setProgress(0);
    setResult(null);
    worker.current?.postMessage({ type: "run", seed: p.seed, n: p.n, scenario: p.scenario, policies: p.policies } satisfies WorkerRequest);
  };
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    if (running) cancel();
    setForm(initial);
    setResult(null);
    setStatus("");
    setProgress(0);
  };
  const download = () => {
    if (!result) return;
    const body = JSON.stringify({ label: "FARE sandbox output (visitor run in the browser; not a research result)", ...result }, null, 1);
    const url = URL.createObjectURL(new Blob([body], { type: "application/json" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `fare-sandbox-seed${result.seed}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const field = (k: keyof Form, label: string, hint: string, step = "any") => (
    <label className="field" htmlFor={`sbx-${k}`}>
      <span>{label}</span>
      <input id={`sbx-${k}`} type="text" inputMode={step === "1" ? "numeric" : "decimal"} autoComplete="off" spellCheck={false} value={form[k] as string}
        aria-describedby={`sbx-${k}-hint`} onChange={(e) => set(k, e.target.value as never)} />
      <small id={`sbx-${k}-hint`}>{hint}</small>
    </label>
  );

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <p className="label-chip chip-sandbox">Sandbox: runs in your browser</p>
      <h2 id="h-sandbox">Booking-market sandbox</h2>
      <p aria-live="polite" className="sandbox-out">{status}</p>
      <p className="note">
        The simulator and the three pricing rules are a port of the research engine, checked against it on fixed
        arrivals. Demand streams use a different random-number generator, so a sandbox seed never reproduces a research
        stream. Sandbox numbers are not research results and are not comparable with the published numbers.
        Policy values are not re-tuned when you change the market; starting from a published cell loads that cell's
        tuned configurations.
      </p>
      <form className="sbx" onSubmit={(e) => { e.preventDefault(); run(); }}>
        <fieldset>
          <legend>Starting point</legend>
          <label className="field wide" htmlFor="sbx-preset">
            <span>Published cell</span>
            <select id="sbx-preset" value={form.preset} onChange={(e) => choosePreset(e.target.value)}>
              {presets.map((p) => (
                <option key={`${p.experiment}|${p.cell_id}`} value={`${p.experiment}|${p.cell_id}`}>
                  {p.experiment} {p.cell_id}
                </option>
              ))}
              <option value="">Neutral sandbox defaults (not tuned)</option>
            </select>
          </label>
          {field("seed", "Seed", "whole number, 1 to 1,000,000", "1")}
          {field("n", "Seasons to simulate", `1 to ${MAX_STREAMS.toLocaleString("en-US")}`, "1")}
        </fieldset>
        <fieldset>
          <legend>Market (assumption values you choose)</legend>
          {field("C", "Capacity (units)", "10 to 500", "1")}
          {field("kappa", "Expected arrivals per unit of capacity", "0.25 to 8")}
          {field("sigma_v", "Valuation dispersion", "log-sd, 0.05 to 1.5")}
          {field("demand_scale", "Actual demand versus forecast", "multiplier, 0.2 to 2.5")}
          <label className="field">
            <span>Arrival order</span>
            <select id="sbx-arrival" value={form.arrival_profile} onChange={(e) => set("arrival_profile", e.target.value as ArrivalProfile)}>
              <option value="linear">Low-valuation early (base)</option>
              <option value="linear_reversed">High-valuation early</option>
              <option value="flat">Flat for both</option>
            </select>
          </label>
          <label className="field check">
            <input id="sbx-shocks" type="checkbox" checked={form.shocks} onChange={(e) => set("shocks", e.target.checked)} />
            <span>Demand shocks (stream multiplier and surges)</span>
          </label>
        </fieldset>
        <fieldset>
          <legend>Pricing rules</legend>
          {field("fix_p", "FIX price", "30 to 600")}
          {field("occ_p0", "OCC starting price", "30 to 600")}
          {field("occ_k", "OCC sensitivity k", "0 to 10; 0 is a fixed price")}
          {field("drp_p0", "DRP starting price", "30 to 600")}
          {field("drp_eta", "DRP step eta", "0 to 2; 0 is a fixed price")}
        </fieldset>
        <div className="controls">
          <button type="submit" disabled={running}>Run sandbox</button>
          <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
          <button type="button" onClick={reset}>Reset</button>
          <button type="button" onClick={download} disabled={!result}>Download sandbox output (JSON)</button>
          {running && <progress max={1} value={progress} aria-label="Sandbox progress" />}
        </div>
      </form>
      {result && <SandboxOutput r={result} />}
    </section>
  );
}

function SandboxOutput({ r }: { r: SandboxResult }) {
  return (
    <div className="sbx-out">
      <h3>Sandbox output, seed {r.seed}, {r.n} seasons</h3>
      <h4>Posted price, first simulated season</h4>
      <Legend keys={[...ARMS]} />
      <TimeChart lines={ARMS.map((a) => ({ key: a, values: r.first[a].prices }))} yLabel="price" label="Sandbox posted price by period for FIX, OCC and DRP" />
      <p className="note">{ARMS.map((a) => pathSummary(a, r.first[a].prices)).join("; ")}.</p>
      <h4>Units left at the end of each period, first simulated season</h4>
      <TimeChart lines={ARMS.map((a) => ({ key: a, values: r.first[a].stock.slice(1) }))} yLabel="units left" label="Sandbox remaining stock by period" yMin={0} />
      <p className="note">
        Units left after the season: {ARMS.map((a) => `${a} ${r.first[a].stock[r.first[a].stock.length - 1]}`).join(", ")}.
      </p>
      <p className="caption" id="sbx-table-cap">Sandbox policy comparison over {r.n} seasons (means; currency units are abstract)</p>
      <div id="sbx-table" className="table-scroll" role="region" aria-labelledby="sbx-table-cap" tabIndex={0}>
        <table className="est" aria-labelledby="sbx-table-cap">
          <thead>
            <tr>
              <th scope="col">Rule</th><th scope="col">Revenue (SD)</th><th scope="col">Sell-through</th>
              <th scope="col">Availability</th><th scope="col">Price volatility</th>
            </tr>
          </thead>
          <tbody>
            {ARMS.map((a) => (
              <tr key={a}>
                <th scope="row">{a}</th>
                <td className="num" data-label="Revenue (SD)">{f0(r.arms[a].revenue_mean)} ({f0(r.arms[a].revenue_sd)})</td>
                <td className="num" data-label="Sell-through">{f3(r.arms[a].sell_through_mean)}</td>
                <td className="num" data-label="Availability">{f3(r.arms[a].availability_mean)}</td>
                <td className="num" data-label="Price volatility">{r.arms[a].volatility_mean.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ul className="plain">
        {r.contrasts.map((c) => (
          <li key={c.arm}>
            {c.arm} minus FIX, paired over the same seasons: {sg(c.mean)} per season, normal 95% interval [{sg(c.lo)}, {sg(c.hi)}];
            the rule earns less than FIX in {(c.share_loses * 100).toFixed(1)}% of seasons.
          </li>
        ))}
      </ul>
    </div>
  );
}
