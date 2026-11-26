// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Hand-written charts: a price timeline (SVG line chart) and interval rows
// (point estimate and interval on a shared axis, drawn with CSS).
import { useEffect, useRef, useState, type ReactNode } from "react";
import { useInView } from "./Board";
import { fmtEstimate, fmtInterval, type Estimate } from "./results";

export const SERIES: Record<string, { cls: string; dash: string; name: string }> = {
  FIX: { cls: "s-fix", dash: "", name: "FIX, fixed price" },
  OCC: { cls: "s-occ", dash: "7 4", name: "OCC, occupancy rule" },
  DRP: { cls: "s-drp", dash: "2 3", name: "DRP, demand-responsive rule" },
  FIX6: { cls: "s-ref", dash: "1 5", name: "FIX6, fixed price on the 6 shared starting prices" },
  FIX_retuned: { cls: "s-ref", dash: "1 5", name: "FIX re-tuned in this cell" },
};

function useWidth<T extends HTMLElement>(fallback = 640): [React.RefObject<T | null>, number] {
  const ref = useRef<T | null>(null);
  const [w, setW] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver((es) => {
      const cw = Math.floor(es[0].contentRect.width);
      if (cw > 0) setW(cw);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w];
}

function niceTicks(lo: number, hi: number, n = 5): number[] {
  const span = hi - lo || 1;
  const raw = span / n;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= n) ?? 10 * mag;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Number(v.toPrecision(10)));
  return out;
}

export interface Line {
  key: string;
  values: number[];
}

/** Line chart over periods 1..T. Series styles come from SERIES (colour and dash). */
export function TimeChart({ lines, yLabel, label, yMin }: { lines: Line[]; yLabel: string; label: string; yMin?: number }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const seen = useInView(ref);
  const H = width < 480 ? 240 : 300;
  const L = 52, R = 14, top = 12, bot = 40;
  const T = Math.max(...lines.map((l) => l.values.length));
  const all = lines.flatMap((l) => l.values);
  const lo0 = yMin ?? Math.min(...all);
  const hi0 = Math.max(...all);
  const pad = (hi0 - lo0) * 0.06 || 1;
  const lo = yMin ?? lo0 - pad, hi = hi0 + pad;
  const sx = (t: number) => L + ((t - 1) / Math.max(T - 1, 1)) * (width - L - R);
  const sy = (v: number) => top + (1 - (v - lo) / (hi - lo)) * (H - top - bot);
  const xt = [1, ...niceTicks(1, T, width < 480 ? 3 : 6).filter((t) => t > 1 && t < T), T];
  return (
    <div ref={ref} className={`chart${seen ? "" : " pending"}`}>
      <svg width={width} height={H} viewBox={`0 0 ${width} ${H}`} role="img" aria-label={label}>
        {niceTicks(lo, hi).map((v) => (
          <g key={v}>
            <line x1={L} x2={width - R} y1={sy(v)} y2={sy(v)} className="grid" />
            <text x={L - 6} y={sy(v) + 4} textAnchor="end" className="tick">{v.toLocaleString("en-US")}</text>
          </g>
        ))}
        {xt.map((t) => (
          <text key={t} x={sx(t)} y={H - bot + 16} textAnchor="middle" className="tick">{t}</text>
        ))}
        <line x1={L} x2={width - R} y1={H - bot} y2={H - bot} className="axis" />
        <text x={(L + width - R) / 2} y={H - 6} textAnchor="middle" className="tick">period (simulation periods)</text>
        <text x={12} y={(top + H - bot) / 2} textAnchor="middle" className="tick" transform={`rotate(-90 12 ${(top + H - bot) / 2})`}>{yLabel}</text>
        <g className="lines">
        {lines.map((l) => {
          const s = SERIES[l.key] ?? SERIES.FIX6;
          const d = l.values.map((v, i) => `${i ? "L" : "M"}${sx(i + 1).toFixed(1)},${sy(v).toFixed(1)}`).join("");
          return <path key={l.key} d={d} className={`line ${s.cls}`} strokeDasharray={s.dash || undefined} />;
        })}
        </g>
      </svg>
    </div>
  );
}

export function Legend({ keys }: { keys: string[] }) {
  return (
    <ul className="legend" aria-label="Line styles">
      {keys.map((k) => {
        const s = SERIES[k] ?? SERIES.FIX6;
        return (
          <li key={k}>
            <svg width="30" height="10" aria-hidden="true">
              <line x1="1" x2="29" y1="5" y2="5" className={`line ${s.cls}`} strokeDasharray={s.dash || undefined} />
            </svg>
            {s.name}
          </li>
        );
      })}
    </ul>
  );
}

/** Rows of estimates, each with its interval drawn on an axis shared by the block. */
export function domainOf(rows: Estimate[]): [number, number] {
  const vals = rows.flatMap((r) => [r.estimate, r.ci_low ?? r.estimate, r.ci_high ?? r.estimate, 0]);
  return [Math.min(...vals), Math.max(...vals)];
}

export function IntervalRows({ rows, caption, kind, id, domain }: { rows: Estimate[]; caption: ReactNode; kind: string; id: string; domain?: [number, number] }) {
  const withCi = rows.filter((r) => r.ci_low !== null && r.ci_high !== null);
  const [lo, hi] = domain ?? domainOf(rows);
  const span = hi - lo || 1;
  const pos = (v: number) => ((v - lo) / span) * 100;
  const showPlot = withCi.length > 0;
  return (
    <>
    <p className="caption" id={`${id}-cap`}>{caption}</p>
    <div id={id} className="table-scroll" role="region" aria-labelledby={`${id}-cap`} tabIndex={0}>
      <table className="est" aria-labelledby={`${id}-cap`}>
        <thead>
          <tr>
            <th scope="col">Quantity</th>
            <th scope="col">Estimate</th>
            <th scope="col">Interval</th>
            {rows.some((r) => r.relative_display) && <th scope="col">Relative, class</th>}
            {showPlot && <th scope="col" className="plotcol">Estimate and interval (0 marked)</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label}>
              <th scope="row">{r.label}</th>
              <td className="num" data-label="Estimate">{fmtEstimate(r)}</td>
              <td className="num" data-label="Interval">{r.ci_low === null ? "none defined" : `${Math.round((r.ci_level ?? 0) * 1000) / 10}% ${fmtInterval(r)}`}</td>
              {rows.some((x) => x.relative_display) && (
                <td data-label="Relative, class">{r.relative_display ?? ""}{r.class_display ? `, ${r.class_display}` : ""}</td>
              )}
              {showPlot && (
                <td className="plotcol" aria-hidden="true">
                  <div className={`track k-${kind}`}>
                    <span className="zero" style={{ left: `${pos(0)}%` }} />
                    {r.ci_low !== null && r.ci_high !== null && (
                      <span className="ci" style={{ left: `${pos(r.ci_low)}%`, width: `${Math.max(pos(r.ci_high) - pos(r.ci_low), 0.6)}%` }} />
                    )}
                    <span className="pt" style={{ left: `${pos(r.estimate)}%` }} />
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </>
  );
}

export function pathSummary(key: string, v: number[]): string {
  const f = (x: number) => x.toFixed(1);
  return `${key}: starts at ${f(v[0])}, ends at ${f(v[v.length - 1])}, lowest ${f(Math.min(...v))}, highest ${f(Math.max(...v))}`;
}
