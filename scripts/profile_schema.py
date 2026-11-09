#!/usr/bin/env python3
"""Formato do profile.json e validação.

Uso: python3 profile_schema.py runs/DATA/profile.json   -> lista campos faltando

Campos desconhecidos = null (não foi possível ler). Valor false/0 = lido e ausente.
Essa diferença importa: a nota não pune o que não foi lido, mas lista como "não verificado".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TEMPLATE: dict = {
    "captured_at": "AAAA-MM-DD",
    "url": None,
    "name": None,
    "headline": "",
    "headline_en": None,            # título do perfil secundário em inglês, se existir
    "location": None,
    "industry": None,
    "custom_url": None,             # true se a URL é linkedin.com/in/nome (sem números aleatórios)
    "photo": None,
    "banner": None,                 # true se é banner próprio (não o padrão azul)
    "verified": None,
    "open_to_work": {"enabled": None, "visibility": None, "titles": [], "locations": [], "remote": None},
    "secondary_language_profile": None,   # true se tem perfil em outro idioma (ex.: EN)
    "about": "",
    "about_en": None,
    "experience": [
        {"title": "", "company": "", "employment_type": None, "location": None,
         "start": "AAAA-MM", "end": None, "description": "", "skills": []}
    ],
    "education": [{"school": "", "degree": "", "field": "", "start": None, "end": None}],
    "skills": [{"name": "", "endorsements": 0, "top": False, "assessment": False}],
    "recommendations_received": [{"date": "AAAA-MM", "author_role": "", "relationship": ""}],
    "recommendations_given": None,
    "certifications": [{"name": "", "issuer": "", "date": None}],
    "projects": [{"name": "", "url": None, "description": ""}],
    "featured": [{"type": "link|post|media", "title": "", "url": None}],
    "languages": [{"name": "", "level": ""}],
    "volunteering": [],
    "honors": [],
    "connected_apps": None,         # apps conectados ao perfil (catálogo de parceiros do LinkedIn)
    "contact": {"website": None, "github": None, "portfolio": None, "email_visible": None},
    "activity": {"posts_90d": None, "comments_90d": None, "reposts_90d": None, "last_post_date": None, "creator_mode": None},
    "metrics": {
        "connections": None, "followers": None,
        "profile_views_90d": None, "search_appearances_7d": None,
        "post_impressions_365d": None,
        "searchers_titles": [], "searchers_companies": [],
        "ssi": {"total": None, "brand": None, "people": None, "insights": None, "relationships": None,
                "industry_rank_pct": None, "network_rank_pct": None},
    },
}

REQUIRED = ["headline", "about", "experience", "skills"]


def merge_defaults(profile: dict, template: dict = TEMPLATE) -> dict:
    out = {}
    for k, v in template.items():
        if k not in profile:
            out[k] = None if not isinstance(v, (dict, list)) else ([] if isinstance(v, list) else merge_defaults({}, v))
        elif isinstance(v, dict) and isinstance(profile[k], dict):
            out[k] = merge_defaults(profile[k], v)
        else:
            out[k] = profile[k]
    for k, v in profile.items():
        out.setdefault(k, v)
    return out


def validate(profile: dict) -> list[str]:
    issues = []
    for k in REQUIRED:
        if not profile.get(k):
            issues.append(f"faltando: {k}")
    for i, e in enumerate(profile.get("experience") or []):
        if not e.get("title") or not e.get("company"):
            issues.append(f"experience[{i}] sem title/company")
        if not e.get("start"):
            issues.append(f"experience[{i}] sem start")
    unknown = [k for k in ("photo", "banner", "custom_url", "open_to_work.enabled", "metrics.ssi.total",
                           "metrics.search_appearances_7d", "activity.posts_90d")
               if _get(profile, k) is None]
    if unknown:
        issues.append("não verificado: " + ", ".join(unknown))
    return issues


def _get(d: dict, dotted: str):
    for part in dotted.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(part)
    return d


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=2))
        sys.exit(0)
    p = merge_defaults(json.loads(Path(sys.argv[1]).read_text()))
    problems = validate(p)
    print("\n".join(problems) if problems else "ok")
