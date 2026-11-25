# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
# M4 evidence audit: keyed check of manuscript Tables 2, 3 and 5 against the exact metrics.csv rows.
# Usage: .venv/bin/python experiments/audit/keyed_table_check.py .
import csv, re, sys
root = sys.argv[1]
ms = open(f"{root}/research/paper/manuscript.md").read().splitlines()
def rows(e):
    return {(r["cell_id"], r["arm"], r["comparator"]): r for r in csv.DictReader(open(f"{root}/research/experiments/{e}/metrics.csv")) if r["metric"] == "revenue"}
def fmt(x, d): return f"{float(x):,.{d}f}"
def cell_str(r, d):
    m = float(r["mean_diff"]); s = ("+" if m > 0 else "") + fmt(m, d)
    return f"{s} [{fmt(r['boot_lo'], d)}, {fmt(r['boot_hi'], d)}]"
checked = bad = 0
def chk(line, exp, label):
    global checked, bad
    checked += 1
    if exp not in line:
        bad += 1; print("MISMATCH", label, exp)
# Table 2
r1 = rows("EXP-001")
for arm, comp, lab in [("OCC","FIX","OCC - FIX"),("DRP","FIX","DRP - FIX"),("OCC","FIX6","OCC - FIX6"),("DRP","FIX6","DRP - FIX6")]:
    line = next(l for l in ms if l.startswith(f"| {lab} |"))
    r = r1[("base", arm, comp)]
    chk(line, f"[{fmt(r['boot_lo'],2)}, {fmt(r['boot_hi'],2)}]", lab+" boot")
    chk(line, f"[{fmt(r['t_lo'],2)}, {fmt(r['t_hi'],2)}]", lab+" t")
    chk(line, f"{100*float(r['relative_effect']):+.2f}%", lab+" rel")
# Table 3
r2 = rows("EXP-002")
for cell in ["sv0.25-k1.0","sv0.25-k2.0","sv0.25-k4.0","sv0.5-k1.0","sv0.5-k2.0","sv0.5-k4.0","sv1.0-k1.0","sv1.0-k2.0","sv1.0-k4.0"]:
    line = next(l for l in ms if l.startswith(f"| {cell} | -"))
    for arm in ("OCC","DRP"):
        r = r2[(cell, arm, "FIX")]
        chk(line, cell_str(r, 1), cell+arm)
        chk(line, f"{100*float(r['relative_effect']):+.2f}%", cell+arm+" rel")
# Table 5
r3 = rows("EXP-003")
names = {"demand x0.6":"demand-x0.6","demand x0.8":"demand-x0.8","demand x1.25":"demand-x1.25","demand x1.6":"demand-x1.6","reversed arrivals":"reversed-arrivals","no shocks":"no-shocks"}
for lab, cell in names.items():
    line = next(l for l in ms if l.startswith(f"| {lab} |"))
    for arm in ("OCC","DRP"):
        for comp in ("FIX","FIX_retuned"):
            if cell == "reversed-arrivals" and comp == "FIX_retuned": continue
            r = r3[(cell, arm, comp)]
            chk(line, cell_str(r, 1), lab+arm+comp)
            chk(line, f"{100*float(r['relative_effect']):+.2f}%", lab+arm+comp+" rel")
print(f"keyed checks: {checked}, mismatches: {bad}")
