#!/usr/bin/env python3
"""Roda a auditoria inteira de uma vez: palavras-chave -> nota -> evolução -> página HTML.

Uso:
  python3 audit.py --profile profile.json --jobs jobs.json --role frontend-senior --out runs/2026-11-09
  python3 audit.py --profile profile.json --jobs jobs.json --role-title "Product Designer" --out runs/D
  python3 audit.py --example            # roda com o perfil fictício de examples/

Opções:
  --rewrites rewrites.json   textos reescritos que entram na página (formato em scripts/render_report.py)
  --previous runs/ANTERIOR   rodada anterior para mostrar a evolução
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = ROOT / "scripts"


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile")
    ap.add_argument("--jobs")
    ap.add_argument("--role", help="id em references/roles (frontend-senior, fullstack)")
    ap.add_argument("--role-title", help="cargo livre; palavras-chave saem só das vagas")
    ap.add_argument("--rewrites")
    ap.add_argument("--previous", help="pasta da rodada anterior (com report.json)")
    ap.add_argument("--out", help="pasta de saída (padrão: runs/AAAA-MM-DD)")
    ap.add_argument("--example", action="store_true", help="usa os arquivos de examples/")
    a = ap.parse_args()

    if a.example:
        ex = ROOT / "examples"
        a.profile, a.jobs, a.rewrites = str(ex / "profile.json"), str(ex / "jobs.json"), str(ex / "rewrites.json")
        a.role = a.role or "frontend-senior"
        a.out = a.out or str(ROOT / "runs" / "example")
    if not (a.profile and a.jobs):
        ap.error("informe --profile e --jobs (ou use --example)")
    if not (a.role or a.role_title):
        ap.error("informe --role ou --role-title")

    out = Path(a.out or ROOT / "runs" / date.today().isoformat())
    out.mkdir(parents=True, exist_ok=True)
    role = ["--role", a.role] if a.role else ["--role-title", a.role_title]

    run(str(S / "profile_schema.py"), a.profile)
    run(str(S / "keywords.py"), "--jobs", a.jobs, *role, "--out", str(out / "keywords.json"))
    run(str(S / "score.py"), "--profile", a.profile, "--keywords", str(out / "keywords.json"),
        "--jobs", a.jobs, "--out", str(out / "report.json"))
    extra = []
    if a.previous:
        run(str(S / "diff_runs.py"), str(Path(a.previous) / "report.json"), str(out / "report.json"),
            "--out", str(out / "diff.json"))
        extra += ["--diff", str(out / "diff.json")]
    if a.rewrites:
        extra += ["--rewrites", a.rewrites]
    run(str(S / "render_report.py"), "--report", str(out / "report.json"), *extra, "--out", str(out / "report.html"))
    print(f"\nPronto. Abra {out / 'report.html'} no navegador.")


if __name__ == "__main__":
    main()
