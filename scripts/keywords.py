#!/usr/bin/env python3
"""Extrai palavras-chave ponderadas de um corpus de vagas (jobs.json).

Uso:
  python3 keywords.py --jobs runs/DATA/jobs.json --role frontend-senior --out runs/DATA/keywords.json
  python3 keywords.py --jobs ... --role-title "Engenheiro de Dados" --out ...   (cargo sem arquivo de role)

Peso de cada termo = fração das vagas que o citam (0–1), com bônus para os termos
"must" do arquivo de cargo. Termos frequentes fora do dicionário vão para
"unmapped" para revisão manual (e podem virar extra_terms no arquivo de cargo).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import textkit as tk  # noqa: E402

ROLES_DIR = Path(__file__).parent.parent / "references" / "roles"


def load_role(role_id: str | None, role_title: str | None) -> dict:
    if role_id:
        path = ROLES_DIR / f"{role_id}.json"
        if not path.exists():
            sys.exit(f"cargo '{role_id}' não encontrado em {ROLES_DIR} (use --role-title para um cargo livre)")
        return json.loads(path.read_text())
    title = role_title or "cargo-alvo"
    return {"id": "custom", "title_pt": title, "title_en": title, "title_aliases": [title.lower()],
            "seniority_terms": [], "must": [], "nice": [], "extra_terms": []}


def filter_jobs(jobs: list[dict], role: dict) -> list[dict]:
    """Usa só as vagas do cargo pedido quando o corpus tem vários cargos."""
    rid = role["id"].split("-")[0]
    picked = [j for j in jobs if j.get("role", "").lower().startswith(rid)]
    return picked or jobs


def build(jobs_doc: dict, role: dict) -> dict:
    jobs = filter_jobs(jobs_doc["jobs"], role)
    extra = role.get("extra_terms", []) + role.get("must", []) + role.get("nice", [])
    df_all: Counter = Counter()
    df_market = {"br": Counter(), "intl": Counter()}
    n_market = Counter()
    unmapped: Counter = Counter()
    known = {tk.strip_accents(v.lower()) for vs in tk.SYNONYMS.values() for v in vs}
    titles = Counter()
    for job in jobs:
        text = f"{job.get('title', '')}\n{job.get('text', '')}"
        terms = set(tk.find_terms(text, extra))
        df_all.update(terms)
        market = job.get("market", "br")
        df_market.setdefault(market, Counter()).update(terms)
        n_market[market] += 1
        titles[tk.strip_accents(job.get("title", "").lower())] += 1
        toks = tk.tokens(text)
        grams = set(toks) | {f"{a} {b}" for a, b in zip(toks, toks[1:])}
        unmapped.update(g for g in grams if g not in known and not g.isdigit() and len(g) > 2)
    n = len(jobs) or 1
    must = {tk.canonical(t) for t in role.get("must", [])}
    terms = []
    for term in set(df_all) | must:
        freq = df_all[term] / n
        weight = min(1.0, freq + (0.25 if term in must else 0.0))
        terms.append({
            "term": term,
            "freq": round(freq, 3),
            "freq_br": round(df_market["br"][term] / n_market["br"], 3) if n_market["br"] else None,
            "freq_intl": round(df_market["intl"][term] / n_market["intl"], 3) if n_market["intl"] else None,
            "must": term in must,
            "weight": round(weight, 3),
        })
    terms.sort(key=lambda x: (-x["weight"], x["term"]))
    min_count = max(3, int(0.2 * n))
    unmapped_top = [{"term": g, "jobs": c} for g, c in unmapped.most_common(400) if c >= min_count][:60]
    return {
        "role": role,
        "n_jobs": len(jobs),
        "n_by_market": dict(n_market),
        "terms": terms,
        "unmapped": unmapped_top,
        "top_titles": titles.most_common(15),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--role")
    ap.add_argument("--role-title")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not a.role and not a.role_title:
        ap.error("informe --role ou --role-title")
    role = load_role(a.role, a.role_title)
    result = build(json.loads(Path(a.jobs).read_text()), role)
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"{result['n_jobs']} vagas, {len(result['terms'])} termos -> {a.out}")
    for t in result["terms"][:20]:
        print(f"  {t['weight']:.2f}  {t['term']}{'  (must)' if t['must'] else ''}")


if __name__ == "__main__":
    main()
