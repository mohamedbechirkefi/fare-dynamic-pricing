// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
// Split-flap boards. Every character shown at rest is published text from
// results.json. While a board flips into place, the intermediate flaps are
// letters and blanks only, never digits, so no number outside the data appears.
import { useEffect, useRef, useState, type RefObject } from "react";
import type { Estimate, Results } from "./results";

export const reducedMotion = () =>
  typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** True once the element has entered the viewport (never resets). */
export function useInView<T extends Element>(ref: RefObject<T | null>, margin = "0px 0px -12% 0px"): boolean {
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || seen) return;
    if (typeof IntersectionObserver === "undefined") { setSeen(true); return; }
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { setSeen(true); io.disconnect(); } }, { rootMargin: margin });
    io.observe(el);
    return () => io.disconnect();
  }, [ref, seen, margin]);
  return seen;
}

const FLAPS = " ABCDEFGHJKLMNPRSTUVWXYZ";
const EASE = "cubic-bezier(0.23, 1, 0.32, 1)";

/** Flip every glyph inside `root` through a few letter flaps to its final character. */
function useFlip(root: RefObject<HTMLElement | null>, play: boolean, rowStagger = 140, colStagger = 34) {
  useEffect(() => {
    const el = root.current;
    if (!el || !play || reducedMotion()) return;
    const timers: number[] = [];
    const glyphs = [...el.querySelectorAll<HTMLElement>(".g")];
    for (const g of glyphs) {
      const final = g.dataset.c ?? "";
      if (final === " ") continue;
      const row = Number(g.dataset.r ?? 0), col = Number(g.dataset.i ?? 0);
      const steps = 3 + ((row + col) % 4);
      const start = row * rowStagger + col * colStagger;
      g.textContent = " ";
      for (let s = 1; s <= steps; s++) {
        timers.push(window.setTimeout(() => {
          g.textContent = s === steps ? final : FLAPS[(col * 7 + row * 5 + s * 11) % FLAPS.length];
          g.animate([{ transform: "rotateX(-78deg)", opacity: 0.55 }, { transform: "rotateX(0deg)", opacity: 1 }], { duration: 70, easing: EASE });
        }, start + s * 62));
      }
    }
    return () => {
      timers.forEach((t) => clearTimeout(t));
      for (const g of glyphs) g.textContent = g.dataset.c ?? "";
    };
  }, [root, play, rowStagger, colStagger]);
}

/** One run of split-flap tiles. The readable text is in the DOM for assistive technology. */
export function Flaps({ text, row = 0, offset = 0, tone }: { text: string; row?: number; offset?: number; tone?: "gain" | "loss" }) {
  return (
    <span className={`flaps${tone ? ` t-${tone}` : ""}`}>
      <span className="sr-only">{text}</span>
      <span aria-hidden="true" className="tiles">
        {[...text].map((c, i) => (
          <span key={i} className="fl"><span className="g" data-c={c} data-r={row} data-i={offset + i}>{c}</span></span>
        ))}
      </span>
    </span>
  );
}

const sign = (s: string | null) => (s && s.trim().startsWith("-") ? "loss" : "gain");

interface HeroRow { rule: string; market: string; rel: string; season: string }

function heroRows(r: Results): HeroRow[] {
  const out: HeroRow[] = [];
  const e1 = r.experiments.find((e) => e.id === "EXP-001");
  for (const lab of ["OCC - FIX", "DRP - FIX"]) {
    const x = e1?.estimates.find((y) => y.label === lab && y.relative_display);
    if (x) out.push({ rule: lab.slice(0, 3), market: "base", rel: x.relative_display!, season: x.display ?? "" });
  }
  const e2 = r.experiments.find((e) => e.id === "EXP-002");
  const rel = (e2?.estimates ?? []).filter((y) => y.relative_display && / - FIX$/.test(y.label));
  const low = rel.reduce<Estimate | null>((m, y) => (m === null || parseFloat(y.relative_display!) < parseFloat(m.relative_display!) ? y : m), null);
  if (low) {
    const [cell, contrast] = low.label.split(": ");
    out.push({ rule: contrast.slice(0, 3), market: cell, rel: low.relative_display!, season: low.display ?? "" });
  }
  return out;
}

/** The hero board: the published base-scenario result and the lowest EXP-002 cell. */
export function HeroBoard({ r }: { r: Results }) {
  const ref = useRef<HTMLDivElement>(null);
  const rows = heroRows(r);
  const [play, setPlay] = useState(false);
  useEffect(() => { const t = window.setTimeout(() => setPlay(true), 250); return () => clearTimeout(t); }, []);
  useFlip(ref, play);
  const pad = (s: string, n: number) => s.padEnd(n, " ");
  const W = { rule: 3, market: Math.max(4, ...rows.map((x) => x.market.length)), rel: Math.max(...rows.map((x) => x.rel.length)), season: Math.max(...rows.map((x) => x.season.length)) };
  return (
    <div className="board hero-board" ref={ref}>
      <table>
        <caption>Revenue against the tuned fixed price, per season</caption>
        <thead>
          <tr><th scope="col">Rule</th><th scope="col">Market</th><th scope="col">Against FIX</th><th scope="col" className="c-season">Currency units</th></tr>
        </thead>
        <tbody>
          {rows.map((x, i) => (
            <tr key={i}>
              <th scope="row"><Flaps text={pad(x.rule, W.rule)} row={i} /></th>
              <td><Flaps text={pad(x.market, W.market)} row={i} offset={4} /></td>
              <td><Flaps text={x.rel.padStart(W.rel, " ")} row={i} offset={5 + W.market} tone={sign(x.rel)} /></td>
              <td className="c-season"><Flaps text={x.season.padStart(W.season, " ")} row={i} offset={6 + W.market + W.rel} tone={sign(x.season)} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="board-foot">
        Measured. Rows 1 and 2: EXP-001, base scenario, 4,000 paired seasons. Row 3: the lowest of the 18 EXP-002
        contrasts. Currency units are abstract; all results are simulated.
      </p>
    </div>
  );
}

/** EXP-002 as a 3 x 3 board: valuation dispersion (rows) by arrivals per unit of capacity (columns). */
export function MatrixBoard({ r }: { r: Results }) {
  const ref = useRef<HTMLDivElement>(null);
  const seen = useInView(ref);
  useFlip(ref, seen, 90, 22);
  const e2 = r.experiments.find((e) => e.id === "EXP-002");
  if (!e2) return null;
  const cells = new Map<string, Estimate[]>();
  for (const x of e2.estimates) {
    if (!x.relative_display || !/^sv[\d.]+-k[\d.]+$/.test(x.group)) continue;
    cells.set(x.group, [...(cells.get(x.group) ?? []), x]);
  }
  const ids = [...cells.keys()];
  const svs = [...new Set(ids.map((g) => g.match(/^sv([\d.]+)/)![1]))].sort((a, b) => Number(a) - Number(b));
  const ks = [...new Set(ids.map((g) => g.match(/-k([\d.]+)$/)![1]))].sort((a, b) => Number(a) - Number(b));
  return (
    <div className="board matrix" ref={ref}>
      <table>
        <caption>EXP-002: revenue of each rule against the fixed price re-tuned in the same cell, in percent</caption>
        <thead>
          <tr>
            <td className="corner"><span>Valuation dispersion</span><span>Arrivals per unit of capacity</span></td>
            {ks.map((k, j) => (
              <th key={k} scope="col">{k}{j === 0 ? <small>loose capacity</small> : j === ks.length - 1 ? <small>tight capacity</small> : null}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {svs.map((sv, i) => (
            <tr key={sv}>
              <th scope="row">{sv}</th>
              {ks.map((k, j) => {
                const g = `sv${sv}-k${k}`;
                const xs = cells.get(g) ?? [];
                return (
                  <td key={k}>
                    {xs.map((x) => {
                      const rule = x.label.split(": ")[1]?.slice(0, 3) ?? "";
                      return (
                        <span className="mrow" key={x.label}>
                          <span className="mrule">{rule}</span>
                          <Flaps text={x.relative_display!.padStart(7, " ")} row={i} offset={j * 8} tone={sign(x.relative_display)} />
                        </span>
                      );
                    })}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
