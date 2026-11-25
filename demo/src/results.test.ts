// SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects a missing price_paths extension", () => {
    const r = good();
    delete r.price_paths;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a price outside the bounds", () => {
    const r = good();
    r.price_paths[0].arms[0].prices[3] = 1e6;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a price path of the wrong length", () => {
    const r = good();
    r.price_paths[0].arms[0].prices.pop();
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an unknown policy family in a cell preset", () => {
    const r = good();
    r.cells[0].policies.OCC.family = "XYZ";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an estimate without a measured or exploratory kind", () => {
    const r = good();
    r.experiments[0].estimates[0].kind = "sandbox";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects empty exploratory checks", () => {
    expect(() => validateResults({ ...good(), exploratory_checks: [] })).toThrow(ResultsError);
  });
  it("keeps null, negative and positive results: every registered experiment is exported", () => {
    const r = validateResults(good());
    expect(r.experiments.map((e) => e.id)).toEqual(["EXP-001", "EXP-002", "EXP-003"]);
    const neg = r.experiments[1].estimates.filter((e) => e.group.startsWith("sv") && e.estimate < 0);
    expect(neg.length).toBe(8);
  });
});
