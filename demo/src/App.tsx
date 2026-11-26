// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
import { useEffect, useMemo, useState } from "react";
import { loadResults, ResultsError, type Estimate, type Experiment, type Results } from "./results";
import { domainOf, IntervalRows, Legend, pathSummary, TimeChart } from "./charts";
import { Sandbox } from "./Sandbox";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <div className="wrap">
          <p className="kicker">FARE · a preregistered simulation study of perishable-stock pricing</p>
          <h1>How do demand and inventory policies affect prices and availability in a simulated market?</h1>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#explorer">Price timelines</a>
            <a href="#results">Results</a>
            <a href="#exploratory">Exploratory checks</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
            <a href="#sandbox">Sandbox</a>
          </nav>
        </div>
      </header>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Published r={state.results} />}
        <Sandbox presets={state.kind === "ready" ? state.results.cells : []} />
      </main>
      <footer className="site">
        <div className="wrap">
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere; sandbox
            settings live only in this page. The page uses no animation.
          </p>
          <p>
            All results are simulated, in abstract currency units, and hold only within the model. Nothing here
            describes, predicts or evaluates any real seller, airline, hotel, fare or pricing system.
          </p>
          <p>
            Mohamed Bechir Kefi, independent researcher. Licence: FARE Source-Available Non-Commercial Research
            License v1.0. Repository: https://github.com/mohamedbechirkefi/fare-dynamic-pricing.
          </p>
        </div>
      </footer>
    </>
  );
}

function Chips() {
  return (
    <ul className="chips" aria-label="How numbers are labelled on this page">
      <li><span className="label-chip chip-measured">Measured</span> published result of a frozen, registered experiment</li>
      <li><span className="label-chip chip-exploratory">Exploratory</span> published post hoc check, never a verdict</li>
      <li><span className="label-chip chip-assumption">Assumption</span> model input chosen before the study, not a measurement</li>
      <li><span className="label-chip chip-sandbox">Sandbox</span> computed in your browser from your settings</li>
    </ul>
  );
}

function groups(e: Experiment): [string, Estimate[]][] {
  const m = new Map<string, Estimate[]>();
  for (const x of e.estimates) m.set(x.group, [...(m.get(x.group) ?? []), x]);
  return [...m.entries()];
}

function cellRows(r: Results, exp: string, cell: string): Estimate[] {
  const e = r.experiments.find((x) => x.id === exp);
  if (!e) return [];
  if (exp === "EXP-001") return e.estimates.filter((x) => x.group.startsWith("Revenue"));
  return e.estimates.filter((x) => x.group === cell);
}

function Explorer({ r }: { r: Results }) {
  const [open, setOpen] = useState(false);
  const [key, setKey] = useState(`${r.price_paths[0].experiment}|${r.price_paths[0].cell_id}`);
  const p = r.price_paths.find((x) => `${x.experiment}|${x.cell_id}` === key) ?? r.price_paths[0];
  const rows = useMemo(() => cellRows(r, p.experiment, p.cell_id), [r, p]);
  const preset = r.cells.find((c) => c.experiment === p.experiment && c.cell_id === p.cell_id);
  const scen = preset ? Object.entries(preset.scenario).map(([k, v]) => `${k} = ${v}`).join(", ") : "";
  return (
    <section id="explorer" aria-labelledby="h-explorer">
      <p className="label-chip chip-measured">Measured</p>
      <h2 id="h-explorer">Price timelines and policy comparisons</h2>
      <p>
        Choose a market cell. The chart shows the price each tuned rule posts in every period of one selling season,
        and the table shows the published revenue comparison for that cell, over 4,000 paired seasons.
      </p>
      <label className="field wide" htmlFor="explorer-cell">
        <span>Market cell</span>
        <select id="explorer-cell" value={key} onChange={(e) => setKey(e.target.value)}>
          {r.price_paths.map((x) => (
            <option key={`${x.experiment}|${x.cell_id}`} value={`${x.experiment}|${x.cell_id}`}>
              {x.experiment} {x.cell_id}
            </option>
          ))}
        </select>
      </label>
      <p className="meta">
        {p.experiment} {p.cell_id}: {scen ? `differs from the base scenario in ${scen}` : "the base scenario"}. Tuned
        policies: {p.arms.map((a) => `${a.arm}(${Object.entries(a.policy.params).filter(([k]) => k !== "weight").map(([k, v]) => `${k} = ${Math.round(v * 100) / 100}`).join(", ")})`).join("; ")}.
      </p>
      <Legend keys={p.arms.map((a) => a.arm)} />
      <TimeChart
        lines={p.arms.map((a) => ({ key: a.arm, values: a.prices }))}
        yLabel="price (currency units)"
        label={`Posted price by period, ${p.experiment} ${p.cell_id}, ${p.stream}`}
      />
      <p className="note">
        Plain-language description: one illustrative season ({p.stream}), not an average. {p.arms.map((a) => pathSummary(a.arm, a.prices)).join("; ")}.
        The same paths are drawn in the committed figure <code>{p.figure_path}</code>.
      </p>
      <details onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}>
        <summary>Price path as a table</summary>
        {open && <div id="explorer-table" className="table-scroll" role="region" aria-label="Price path table" tabIndex={0}>
          <table>
            <thead>
              <tr><th scope="col">Period</th>{p.arms.map((a) => <th key={a.arm} scope="col">{a.arm}</th>)}</tr>
            </thead>
            <tbody>
              {p.arms[0].prices.map((_, t) => (
                <tr key={t}><th scope="row">{t + 1}</th>{p.arms.map((a) => <td key={a.arm} className="num">{a.prices[t].toFixed(2)}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>}
      </details>
      {rows.length > 0 && (
        <IntervalRows id="explorer-rows" rows={rows} kind="measured" caption={`${p.experiment} ${p.cell_id}: mean paired revenue difference per season (currency units)`} />
      )}
    </section>
  );
}

function ExperimentPanel({ e, kind }: { e: Experiment; kind: "measured" | "exploratory" }) {
  // One axis per unit within an experiment, so intervals are comparable across cells.
  const separate = (g: string) => g.startsWith("Interaction") || g.startsWith("Secondary");
  const dom = (unit: string) => domainOf(e.estimates.filter((x) => x.unit === unit && x.ci_low !== null && !separate(x.group)));
  const domainFor = (rows: Estimate[]) =>
    separate(rows[0].group) ? undefined : dom(rows[0].unit);
  return (
    <article className={`panel k-${kind}`} aria-labelledby={`h-${e.id}`}>
      <p className={`label-chip chip-${kind}`}>{kind === "measured" ? "Measured" : "Exploratory"}</p>
      <h3 id={`h-${e.id}`}>{e.id}: {e.title}</h3>
      <p><span className="badge">{e.status}</span></p>
      <p><strong>{kind === "measured" ? "Verdict under the frozen rule:" : "Reading (not a verdict):"}</strong> {e.verdict}</p>
      {groups(e).map(([g, rows], i) => (
        <IntervalRows key={g} id={`rows-${e.id}-${i}`} rows={rows} kind={kind} caption={g} domain={domainFor(rows)} />
      ))}
      {e.notes.map((n, i) => <p key={i} className="note">{n}</p>)}
      <p className="meta">
        Source: <code>{e.report_path}</code>
        {e.claim_ids.length > 0 && <> · Claims register: {e.claim_ids.join(", ")}</>}
      </p>
    </article>
  );
}

function Published({ r }: { r: Results }) {
  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Overview</h2>
        <p className="status-label"><strong>Status.</strong> {r.status_label}</p>
        <p>
          A seller holds a fixed stock of a perishable product: whatever is unsold at the deadline is worth nothing.
          The study compares a tuned fixed price (FIX) with two simple dynamic rules, an occupancy rule (OCC) that
          raises the price when stock sells faster than time passes, and a demand-responsive rule (DRP) that steers
          the sales rate toward clearing the stock. Every policy sees exactly the same simulated buyers.
        </p>
        <p>
          In short: the dynamic rules earn a few percent more than the fixed price at the base scenario, lose in every
          market where capacity is loose, and keep a relevant advantage over a correctly re-tuned fixed price only when
          demand exceeds the forecast or, for OCC, when the arrival order is reversed. Gains, losses and null-like results are shown below with the same weight.
        </p>
        <Chips />
      </section>

      <Explorer r={r} />

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          Every number below is the exact text printed in the manuscript, exported from the committed results at
          revision <code>{r.code_revision.slice(0, 12)}</code>. Each row shows its interval; the bar plots the estimate
          and interval on one axis shared by all revenue rows of the experiment, with 0 marked. The smallest effect size of interest is 1%
          of the fixed-price revenue in each cell.
        </p>
        {r.experiments.map((e) => <ExperimentPanel key={e.id} e={e} kind="measured" />)}
      </section>

      <section id="exploratory" aria-labelledby="h-exploratory">
        <h2 id="h-exploratory">Exploratory checks (post hoc)</h2>
        <p className="note">
          These checks (journal J-0012) were computed after the confirmatory results were seen. They qualify the
          interpretation and never change a frozen verdict.
        </p>
        {r.exploratory_checks.map((e) => <ExperimentPanel key={e.id} e={e} kind="exploratory" />)}
        {r.display_exceptions.length > 0 && (
          <p className="note">
            Some exploratory intervals are not printed in the manuscript; they come from{" "}
            <code>results/exploratory/m4_audit_sensitivity.json</code>, rounded to 1 decimal, and are listed as display
            exceptions in the exported results.
          </p>
        )}
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <p className="label-chip chip-assumption">Assumption</p>
        <h2 id="h-assumptions">Assumptions</h2>
        <p className="note">Base scenario values. They are planning choices, not calibrated estimates of any real market.</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>{a.value} <span className="meta">({a.source})</span></dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          Three experiments were registered and their protocols frozen by the owner before any evaluation stream
          existed. Each policy family is tuned on the same tuning streams with an equal budget of 36 configurations and
          evaluated on disjoint evaluation streams, with every policy replaying the same streams (common random
          numbers), so every comparison is paired. EXP-001 compares the rules at the base scenario, EXP-002 varies
          valuation dispersion and demand-to-capacity tightness, and EXP-003 tests whether the base result survives
          demand misspecification. The manuscript is <code>research/paper/manuscript.md</code>; each experiment has its
          own report.
        </p>
        <h3>Limitations</h3>
        <ol className="limits">
          {r.limitations.map((l, i) => {
            const cut = l.indexOf(". ");
            return cut > 0 ? <li key={i}><strong>{l.slice(0, cut + 1)}</strong>{l.slice(cut + 1)}</li> : <li key={i}>{l}</li>;
          })}
        </ol>
        <details>
          <summary>Source files and SHA-256 hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}><code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code></li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}
