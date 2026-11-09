#!/usr/bin/env python3
"""Compara duas rodadas (report.json) e mostra a evolução.

Uso: python3 diff_runs.py runs/ANTES/report.json runs/DEPOIS/report.json [--out diff.json]
     python3 diff_runs.py --latest ~/Documents/linkedin-audit/runs   (compara as 2 últimas)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def diff(before: dict, after: dict) -> dict:
    secs = {}
    for k, sec in after["sections"].items():
        b = before["sections"].get(k, {}).get("score")
        a = sec["score"]
        secs[k] = {"label": sec["label"], "before": b, "after": a,
                   "delta": None if a is None or b is None else round(a - b, 1)}
    bgaps = {g["id"] for g in before["gaps"]}
    agaps = {g["id"] for g in after["gaps"]}
    return {
        "before_date": before["generated_at"], "after_date": after["generated_at"],
        "overall_before": before["overall"], "overall_after": after["overall"],
        "overall_delta": round(after["overall"] - before["overall"], 1),
        "sections": secs,
        "fixed": sorted(bgaps - agaps),
        "new_gaps": sorted(agaps - bgaps),
        "keywords_gained": sorted(set(after["keywords"]["hit"]) - set(before["keywords"]["hit"])),
        "keywords_lost": sorted(set(before["keywords"]["hit"]) - set(after["keywords"]["hit"])),
    }


def latest_two(runs: Path) -> tuple[Path, Path]:
    reps = sorted(p for p in runs.glob("*/report.json"))
    if len(reps) < 2:
        raise SystemExit("precisa de pelo menos 2 rodadas com report.json")
    return reps[-2], reps[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", nargs="?")
    ap.add_argument("after", nargs="?")
    ap.add_argument("--latest")
    ap.add_argument("--out")
    a = ap.parse_args()
    b, af = latest_two(Path(a.latest).expanduser()) if a.latest else (Path(a.before), Path(a.after))
    d = diff(json.loads(b.read_text()), json.loads(af.read_text()))
    if a.out:
        Path(a.out).write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"{d['before_date']} → {d['after_date']}: {d['overall_before']} → {d['overall_after']} ({d['overall_delta']:+})")
    for s in d["sections"].values():
        print(f"  {s['label']:<45} {s['before']} → {s['after']}  ({s['delta']:+})" if s["delta"] is not None else f"  {s['label']}: {s['after']}")
    print("Resolvidos:", ", ".join(d["fixed"]) or "—")
    print("Palavras-chave novas:", ", ".join(d["keywords_gained"]) or "—")


if __name__ == "__main__":
    main()
