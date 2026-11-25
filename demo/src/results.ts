// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
  /** FARE extensions: row group (cell or block), relative effect and SESOI class as printed, and the label kind. */
  group: string;
  relative_display: string | null;
  class_display: string | null;
  kind: "measured" | "exploratory";
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  exploratory_checks: Experiment[];
  price_paths: PricePath[];
  cells: CellPreset[];
  display_exceptions: DisplayException[];
}

export interface PolicySpec {
  family: "FIX" | "OCC" | "DRP";
  params: Record<string, number>;
}

export interface PricePath {
  experiment: string;
  cell_id: string;
  stream: string;
  figure_path: string;
  figure_sha256: string;
  T: number;
  p_min: number;
  p_max: number;
  arms: { arm: string; policy: PolicySpec; prices: number[] }[];
}

export interface CellPreset {
  experiment: string;
  cell_id: string;
  scenario: Record<string, number | string>;
  policies: Record<string, PolicySpec>;
}

export interface DisplayException {
  experiment: string;
  label: string;
  field: string;
  value: string;
  note: string;
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function optStr(o: Obj, k: string, where: string): string | null {
  const v = o[k];
  if (v === null || v === undefined) return null;
  if (typeof v !== "string" || v.length === 0) throw new ResultsError(`${where}.${k}: expected a string or null`);
  return v;
}

function badKind(where: string): never {
  throw new ResultsError(`${where}.kind: expected "measured" or "exploratory"`);
}

function policy(v: unknown, where: string): PolicySpec {
  const o = obj(v, where);
  const fam = o.family;
  const need: Record<string, string[]> = { FIX: ["p"], OCC: ["p0", "k"], DRP: ["p0", "eta"] };
  if (typeof fam !== "string" || !(fam in need)) throw new ResultsError(`${where}.family: unknown policy family`);
  const p = obj(o.params, `${where}.params`);
  const params: Record<string, number> = {};
  for (const [k, x] of Object.entries(p)) {
    if (typeof x !== "number" || !Number.isFinite(x) || x < 0) throw new ResultsError(`${where}.params.${k}: expected a finite non-negative number`);
    params[k] = x;
  }
  for (const k of need[fam]) if (!(k in params)) throw new ResultsError(`${where}.params.${k}: missing`);
  return { family: fam as PolicySpec["family"], params };
}

function experiment(v: unknown, w: string): Experiment {
  const e = obj(v, w);
  return {
    id: str(e, "id", w),
    title: str(e, "title", w),
    status: str(e, "status", w),
    verdict: str(e, "verdict", w),
    estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
    claim_ids: strArr(e, "claim_ids", w),
    report_path: str(e, "report_path", w),
    notes: strArr(e, "notes", w),
  };
}

function pricePath(v: unknown, w: string): PricePath {
  const o = obj(v, w);
  const T = num(o, "T", w) as number;
  const lo = num(o, "p_min", w) as number;
  const hi = num(o, "p_max", w) as number;
  if (!Number.isInteger(T) || T < 2 || lo <= 0 || lo > hi) throw new ResultsError(`${w}: bad horizon or price bounds`);
  const sha = str(o, "figure_sha256", w);
  if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`${w}.figure_sha256: not a sha256`);
  const arms = arr(o, "arms", w).map((x, j) => {
    const ww = `${w}.arms[${j}]`;
    const a = obj(x, ww);
    const prices = arr(a, "prices", ww).map((p, t) => {
      if (typeof p !== "number" || !Number.isFinite(p) || p < lo - 1e-6 || p > hi + 1e-6) {
        throw new ResultsError(`${ww}.prices[${t}]: expected a price within the bounds`);
      }
      return p;
    });
    if (prices.length !== T) throw new ResultsError(`${ww}.prices: expected ${T} periods`);
    return { arm: str(a, "arm", ww), policy: policy(a.policy, `${ww}.policy`), prices };
  });
  if (arms.length === 0) throw new ResultsError(`${w}.arms: empty`);
  return {
    experiment: str(o, "experiment", w), cell_id: str(o, "cell_id", w), stream: str(o, "stream", w),
    figure_path: str(o, "figure_path", w), figure_sha256: sha, T, p_min: lo, p_max: hi, arms,
  };
}

function cellPreset(v: unknown, w: string): CellPreset {
  const o = obj(v, w);
  const sc = obj(o.scenario, `${w}.scenario`);
  const scenario: Record<string, number | string> = {};
  for (const [k, x] of Object.entries(sc)) {
    if (typeof x === "string" || (typeof x === "number" && Number.isFinite(x))) scenario[k] = x;
    else throw new ResultsError(`${w}.scenario.${k}: expected a finite number or a string`);
  }
  const pp = obj(o.policies, `${w}.policies`);
  const policies: Record<string, PolicySpec> = {};
  for (const [k, x] of Object.entries(pp)) policies[k] = policy(x, `${w}.policies.${k}`);
  for (const k of ["FIX", "OCC", "DRP"]) if (!(k in policies)) throw new ResultsError(`${w}.policies.${k}: missing`);
  return { experiment: str(o, "experiment", w), cell_id: str(o, "cell_id", w), scenario, policies };
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
    group: typeof o.group === "string" ? o.group : "",
    relative_display: optStr(o, "relative_display", where),
    class_display: optStr(o, "class_display", where),
    kind: o.kind === "exploratory" ? "exploratory" : o.kind === "measured" ? "measured" : badKind(where),
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

function nonEmpty(a: unknown[], where: string): unknown[] {
  if (a.length === 0) throw new ResultsError(`results.${where}: empty`);
  return a;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => experiment(v, `experiments[${i}]`));
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    exploratory_checks: nonEmpty(arr(o, "exploratory_checks", "results"), "exploratory_checks").map((v, i) =>
      experiment(v, `exploratory_checks[${i}]`)),
    price_paths: nonEmpty(arr(o, "price_paths", "results"), "price_paths").map((v, i) => pricePath(v, `price_paths[${i}]`)),
    cells: nonEmpty(arr(o, "cells", "results"), "cells").map((v, i) => cellPreset(v, `cells[${i}]`)),
    display_exceptions: arr(o, "display_exceptions", "results").map((v, i) => {
      const w = `display_exceptions[${i}]`;
      const d = obj(v, w);
      return { experiment: str(d, "experiment", w), label: str(d, "label", w), field: str(d, "field", w),
               value: str(d, "value", w), note: str(d, "note", w) };
    }),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
