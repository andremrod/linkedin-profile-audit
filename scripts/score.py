#!/usr/bin/env python3
"""Dá nota 0–100 ao perfil por seção e lista as lacunas por impacto/esforço.

Uso:
  python3 score.py --profile runs/D/profile.json --keywords runs/D/keywords.json \
                   [--jobs runs/D/jobs.json] [--rubric references/rubric.json] --out runs/D/report.json

Cada critério devolve uma nota 0–1. Critério com dado null (não lido) fica fora da
média da seção e aparece em "unverified" — não é punido nem premiado.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import textkit as tk  # noqa: E402
from profile_schema import merge_defaults  # noqa: E402

RUBRIC = Path(__file__).parent.parent / "references" / "rubric.json"


class Section:
    def __init__(self, key: str):
        self.key = key
        self.items: list[dict] = []

    def add(self, cid: str, label: str, score, weight: float, fix: str = "", effort: int = 1, detail: str = ""):
        """score None = não verificado. effort 1 (minutos) .. 3 (semanas)."""
        self.items.append({"id": cid, "label": label, "score": None if score is None else round(max(0.0, min(1.0, score)), 3),
                           "weight": weight, "fix": fix, "effort": effort, "detail": detail})

    def total(self):
        known = [i for i in self.items if i["score"] is not None]
        w = sum(i["weight"] for i in known)
        return round(100 * sum(i["score"] * i["weight"] for i in known) / w, 1) if w else None


def months_between(a: str, b: str) -> int:
    ay, am = (int(x) for x in a[:7].split("-")) if len(a) >= 7 else (int(a[:4]), 1)
    by, bm = (int(x) for x in b[:7].split("-")) if len(b) >= 7 else (int(b[:4]), 1)
    return (by - ay) * 12 + (bm - am)


def ratio(value, target):
    if value is None:
        return None
    return min(1.0, value / target) if target else 1.0


def boolscore(v):
    return None if v is None else (1.0 if v else 0.0)


def keyword_coverage(text: str, terms: list[dict], extra: list[str], top_n: int | None = None) -> tuple[float, list[str], list[str]]:
    pool = terms[:top_n] if top_n else terms
    found = set(tk.find_terms(text, extra))
    total = sum(t["weight"] for t in pool) or 1
    hit = [t["term"] for t in pool if t["term"] in found]
    miss = [t["term"] for t in pool if t["term"] not in found]
    return sum(t["weight"] for t in pool if t["term"] in found) / total, hit, miss


def profile_text(p: dict) -> str:
    parts = [p.get("headline") or "", p.get("about") or "", p.get("headline_en") or "", p.get("about_en") or ""]
    for e in p.get("experience") or []:
        parts += [e.get("title", ""), e.get("description", ""), " ".join(e.get("skills") or [])]
    parts += [s.get("name", "") for s in p.get("skills") or []]
    parts += [c.get("name", "") for c in p.get("certifications") or []]
    parts += [f"{x.get('name', '')} {x.get('description', '')}" for x in p.get("projects") or []]
    return "\n".join(parts)


def score(profile: dict, kw: dict, rubric: dict, jobs: list[dict] | None = None, today: str | None = None) -> dict:
    p = merge_defaults(profile)
    th = rubric["thresholds"]
    role = kw["role"]
    terms = kw["terms"]
    extra = role.get("extra_terms", []) + role.get("must", []) + role.get("nice", [])
    today = today or date.today().isoformat()
    top_terms = [t["term"] for t in terms[:15]]
    sections: dict[str, Section] = {k: Section(k) for k in rubric["sections"]}

    # ---------------- visibilidade na busca ----------------
    s = sections["visibilidade_busca"]
    head = p.get("headline") or ""
    head_n = tk.norm(head)
    aliases = [tk.strip_accents(a.lower()) for a in role.get("title_aliases", []) + [role.get("title_pt", ""), role.get("title_en", "")] if a]
    has_title = any(a and a in head_n for a in aliases)
    head_terms = set(tk.find_terms(head, extra))
    head_kw = len(head_terms & set(top_terms))
    s.add("headline_title", "Título traz o cargo-alvo com o nome que recrutadores buscam", 1.0 if has_title else 0.0, 3,
          f"Começar o título por '{role['title_pt']}' ou '{role['title_en']}'.", 1, f"título atual: “{head}”")
    s.add("headline_keywords", f"Título com ≥{th['headline_min_keywords']} das palavras-chave mais pedidas",
          ratio(head_kw, th["headline_min_keywords"]), 3,
          "Incluir no título as tecnologias mais pedidas: " + ", ".join(t for t in top_terms if t not in head_terms)[:160], 1,
          f"no título: {', '.join(sorted(head_terms)) or 'nenhuma'}")
    s.add("headline_length", "Título usa o espaço (120–220 caracteres)",
          1.0 if 120 <= len(head) <= th["headline_max_chars"] else (len(head) / 120 if len(head) < 120 else 0.7), 1,
          "Usar 120–220 caracteres: cargo | stack | resultado/proposta de valor.", 1, f"{len(head)} caracteres")
    seniority = [tk.strip_accents(x) for x in role.get("seniority_terms", [])]
    if seniority:
        s.add("headline_seniority", "Senioridade explícita no título", 1.0 if any(f" {x}" in head_n for x in seniority) else 0.0, 1,
              "Escrever a senioridade (Sênior / Senior) no título — é filtro comum na busca.", 1)
    s.add("photo", "Foto de perfil", boolscore(p["photo"]), 2, "Adicionar foto profissional, rosto ocupando ~60% do quadro.", 1)
    s.add("banner", "Banner próprio", boolscore(p["banner"]), 1, "Trocar o banner padrão por um com stack e proposta de valor.", 1)
    s.add("location", "Localização preenchida", boolscore(bool(p["location"]) if p["location"] is not None else None), 2,
          "Preencher cidade/estado — recrutadores filtram por local.", 1)
    s.add("custom_url", "URL personalizada", boolscore(p["custom_url"]), 1, "Trocar a URL por linkedin.com/in/seu-nome.", 1)
    otw = p["open_to_work"]
    s.add("open_to_work", "Open to Work ligado (visível só para recrutadores)", boolscore(otw.get("enabled")), 2,
          "Ligar 'Aberto a trabalho' com visibilidade 'Somente recrutadores', com cargos e 'Remoto'.", 1)
    if otw.get("enabled"):
        otw_titles = len(otw.get("titles") or [])
        s.add("otw_titles", "Open to Work com até 5 cargos e local/remoto", ratio(otw_titles, 3) * (1 if otw.get("remote") or otw.get("locations") else 0.6), 1,
              "Cadastrar 3–5 cargos (PT e EN) e marcar Remoto + localizações.", 1)
    s.add("verified", "Selo de verificação", boolscore(p["verified"]), 1, "Verificar identidade/e-mail corporativo no LinkedIn (selo).", 1)

    # ---------------- sobre ----------------
    s = sections["sobre"]
    about = p.get("about") or ""
    first = about[:300]
    s.add("about_exists", "Sobre preenchido", 1.0 if about.strip() else 0.0, 2, "Escrever um Sobre de 1.200–2.400 caracteres.", 2)
    if about.strip():
        L = len(about)
        s.add("about_length", f"Tamanho do Sobre ({th['about_min_chars']}–{th['about_max_chars']} caracteres)",
              1.0 if th["about_min_chars"] <= L <= th["about_max_chars"] else min(1.0, L / th["about_min_chars"]), 1,
              "Ajustar o Sobre para 1.000–2.600 caracteres.", 2, f"{L} caracteres")
        hook_terms = set(tk.find_terms(first, extra))
        s.add("about_hook", "Cargo e palavras-chave nas 3 primeiras linhas (aparecem antes do 'ver mais')",
              min(1.0, (0.5 if any(a in tk.norm(first) for a in aliases) else 0) + 0.5 * ratio(len(hook_terms & set(top_terms)), 3)), 2,
              "Abrir o Sobre com cargo + anos de experiência + 3 tecnologias principais.", 1)
        s.add("about_metrics", "Resultados com números no Sobre", 1.0 if tk.has_metric(about) else 0.0, 2,
              "Citar 2–3 resultados com número (ex.: 'reduzi o tempo de carregamento em [X]%').", 2)
        cov, _, _ = keyword_coverage(about, terms, extra, 25)
        s.add("about_keywords", "Palavras-chave das vagas no Sobre", min(1.0, cov / 0.6), 2,
              "Incluir uma linha 'Stack:' com as tecnologias mais pedidas.", 1, f"cobertura {cov:.0%} das 25 principais")
        cta = any(w in tk.norm(about) for w in ("contato", "fale comigo", "mensagem", "e-mail", "email", "reach out", "contact", "dm", "vamos conversar", "let's talk", "lets talk"))
        s.add("about_cta", "Chamada para contato no final", 1.0 if cta else 0.0, 1,
              "Terminar com chamada: 'Aberto a oportunidades — fale comigo por mensagem/e-mail'.", 1)
    s.add("about_en", "Versão em inglês (perfil secundário ou bloco EN)",
          1.0 if (p.get("about_en") or p.get("secondary_language_profile")) else (0.0 if p.get("secondary_language_profile") is not None or about else None), 2,
          "Criar o perfil secundário em inglês (Perfil > Adicionar perfil em outro idioma).", 2)

    # ---------------- experiência ----------------
    s = sections["experiencia"]
    exps = p.get("experience") or []
    s.add("exp_exists", "Experiências cadastradas", 1.0 if exps else 0.0, 2, "Cadastrar as experiências.", 2)
    if exps:
        cur = exps[0]
        cur_n = tk.norm(cur.get("title", ""))
        s.add("exp_current_title", "Cargo atual com nome de mercado (o que entra no filtro 'cargo atual')",
              1.0 if any(a in cur_n for a in aliases) else 0.3, 3,
              f"Usar nome padrão no cargo atual, ex.: '{role['title_en']}' / '{role['title_pt']}'.", 1, f"cargo atual: “{cur.get('title', '')}”")
        recent = exps[:3]
        desc_ok = [len(e.get("description") or "") >= th["experience_min_desc_chars"] for e in recent]
        s.add("exp_descriptions", f"Descrição com ≥{th['experience_min_desc_chars']} caracteres nas 3 últimas",
              sum(desc_ok) / len(recent), 3, "Escrever 3–6 tópicos por experiência recente.", 2,
              f"{sum(desc_ok)}/{len(recent)} com descrição completa")
        bullets = [b for e in recent for b in tk.split_bullets(e.get("description") or "")]
        with_metric = sum(tk.has_metric(b) for b in bullets)
        r = with_metric / len(bullets) if bullets else 0.0
        s.add("exp_metrics", "Tópicos com números (impacto mensurável)", min(1.0, r / th["bullet_metric_ratio_target"]), 3,
              "Reescrever tópicos como verbo + o que fez + resultado com número.", 2,
              f"{with_metric}/{len(bullets)} tópicos com número")
        skills_tagged = sum(1 for e in recent if e.get("skills"))
        s.add("exp_skills", "Competências marcadas em cada experiência", skills_tagged / len(recent), 2,
              "Marcar 5+ competências em cada experiência (liga a experiência às competências na busca).", 1)
        cov, _, _ = keyword_coverage(" ".join((e.get("title", "") + " " + (e.get("description") or "")) for e in recent), terms, extra, 25)
        s.add("exp_keywords", "Palavras-chave das vagas nas experiências", min(1.0, cov / 0.6), 2,
              "Citar nas experiências as tecnologias reais que você usou e que as vagas pedem.", 2, f"cobertura {cov:.0%}")
        gaps = []
        for newer, older in zip(exps, exps[1:]):
            if older.get("end") and newer.get("start"):
                gap = months_between(older["end"], newer["start"])
                if gap > 6:
                    gaps.append(f"{older['end']}→{newer['start']}")
        s.add("exp_gaps", "Sem lacunas longas sem explicação (>6 meses)", 1.0 if not gaps else 0.5, 1,
              "Explicar lacunas (estudo, projeto próprio, freelancer) como experiência.", 1, ", ".join(gaps))
        s.add("exp_education", "Formação cadastrada", 1.0 if p.get("education") else 0.0, 1, "Cadastrar formação/cursos.", 1)

    # ---------------- competências ----------------
    s = sections["competencias"]
    skills = p.get("skills") or []
    names = [x.get("name", "") for x in skills]
    s.add("skills_count", f"Quantidade de competências (meta {th['skills_target']}, máx. {th['skills_max']})",
          ratio(len(skills), th["skills_target"]), 2, f"Adicionar competências até ~{th['skills_target']} (limite {th['skills_max']}).", 1, f"{len(skills)} cadastradas")
    cov, hit, miss = keyword_coverage("\n".join(names), terms, extra, 30)
    s.add("skills_coverage", "Competências cobrem as 30 palavras-chave mais pedidas", cov, 3,
          "Adicionar como competência: " + ", ".join(miss[:12]), 1, f"cobertura {cov:.0%}")
    tops = [x for x in skills if x.get("top")]
    top_terms_hit = len(set(tk.find_terms("\n".join(x["name"] for x in tops), extra)) & set(top_terms[:10]))
    s.add("skills_top", "5 competências principais fixadas e alinhadas ao cargo",
          (ratio(len(tops), th["top_skills"]) or 0) * 0.5 + 0.5 * ratio(top_terms_hit, min(5, th["top_skills"])), 2,
          "Fixar como principais as 5 mais pedidas: " + ", ".join(top_terms[:5]), 1,
          "principais: " + (", ".join(x["name"] for x in tops) or "nenhuma"))
    endorsed = [x for x in skills if (x.get("endorsements") or 0) >= 5]
    s.add("skills_endorsements", "Competências com ≥5 endossos (das 10 primeiras)",
          ratio(len([x for x in skills[:10] if (x.get('endorsements') or 0) >= 5]), 10) if skills else 0.0, 1,
          "Pedir endossos a colegas nas competências principais.", 2, f"{len(endorsed)} com ≥5 endossos")

    # ---------------- prova social ----------------
    s = sections["prova_social"]
    recs = p.get("recommendations_received") or []
    s.add("recs_count", f"Recomendações recebidas (meta {th['recommendations_target']})", ratio(len(recs), th["recommendations_target"]), 3,
          "Pedir recomendações a gestor, colega de produto/design e alguém que você mentorou.", 3, f"{len(recs)} recebidas")
    recent_recs = [r for r in recs if r.get("date") and months_between(r["date"], today) <= th["recommendation_recent_months"]]
    if recs:
        s.add("recs_recent", "Recomendações dos últimos 3 anos", ratio(len(recent_recs), 2), 1, "Pedir 1–2 recomendações do emprego atual.", 3)
    s.add("certs", "Certificações relevantes", ratio(len(p.get("certifications") or []), 2), 1,
          "Adicionar 1–2 certificações relevantes (ex.: AWS, Meta Front-End, cursos com certificado).", 3)
    s.add("featured", "Destaques com trabalho (portfólio, GitHub, artigo, projeto)", ratio(len(p.get("featured") or []), 3), 2,
          "Colocar 3 itens em Destaques: portfólio/GitHub, um projeto com resultado, um artigo/post técnico.", 2)
    s.add("projects", "Projetos cadastrados", ratio(len(p.get("projects") or []), 2), 1, "Cadastrar 2+ projetos com link e stack.", 2)
    contact = p.get("contact") or {}
    s.add("links", "Site/GitHub/portfólio no perfil", 1.0 if any(contact.get(k) for k in ("website", "github", "portfolio")) else 0.0, 1,
          "Adicionar link de GitHub/portfólio em Informações de contato e no Sobre.", 1)
    apps = p.get("connected_apps")
    s.add("connected_apps", "Apps conectados ao perfil (os parceiros aparecem no Hiring Assistant 2)",
          None if apps is None else ratio(len(apps), 1), 2,
          "Conectar os apps parceiros que você usa em Perfil > Adicionar seção > Apps conectados (a lista muda; o GitHub não estava nela em ago/2026).", 1)
    langs = [tk.strip_accents((l.get("name") or "").lower()) for l in p.get("languages") or []]
    s.add("languages", "Idiomas cadastrados (inglês com nível)", 1.0 if any(x in ("ingles", "english") for x in langs) else 0.0, 2,
          "Cadastrar Inglês com o nível real (vagas de fora filtram por isso).", 1)

    # ---------------- atividade ----------------
    s = sections["atividade"]
    act, met = p["activity"], p["metrics"]
    s.add("posts", f"Posts nos últimos 90 dias (meta {th['posts_90d_target']})", ratio(act.get("posts_90d"), th["posts_90d_target"]), 2,
          "Postar 1x a cada 2 semanas sobre o que você resolveu no trabalho ou estudou.", 3)
    s.add("comments", f"Comentários nos últimos 90 dias (meta {th['comments_90d_target']})", ratio(act.get("comments_90d"), th["comments_90d_target"]), 1,
          "Comentar com conteúdo em posts da sua área 2–3x por semana.", 2)
    s.add("connections", f"Conexões (meta {th['connections_target']}+)", ratio(met.get("connections"), th["connections_target"]), 1,
          "Conectar com recrutadores tech e pessoas das empresas-alvo.", 3)
    ssi = (met.get("ssi") or {}).get("total")
    s.add("ssi", f"SSI (meta {th['ssi_target']})", ratio(ssi, th["ssi_target"]), 1,
          "Subir o SSI: perfil completo (marca), achar pessoas certas, interagir com conteúdo, manter relações.", 3)

    # ---------------- busca por IA ----------------
    s = sections["busca_ia"]
    full = profile_text(p)
    cov_all, hit_all, miss_all = keyword_coverage(full, terms, extra, 40)
    s.add("kw_coverage", "Cobertura ponderada das 40 palavras-chave das vagas no perfil todo", min(1.0, cov_all / 0.8), 4,
          "Cobrir as palavras-chave que faltam (só as que você domina): " + ", ".join(miss_all[:12]), 2, f"cobertura {cov_all:.0%}")
    must_terms = [t["term"] for t in terms if t.get("must")]
    must_hit = [t for t in must_terms if t in set(tk.find_terms(full, extra))]
    s.add("kw_must", "Todos os requisitos obrigatórios do cargo aparecem", (len(must_hit) / len(must_terms)) if must_terms else None, 3,
          "Faltam requisitos centrais: " + ", ".join(t for t in must_terms if t not in must_hit), 2)
    sim = None
    if jobs:
        vecs = tk.tfidf_vectors([full] + [f"{j.get('title', '')} {j.get('text', '')}" for j in jobs])
        sims = sorted((tk.cosine(vecs[0], v) for v in vecs[1:]), reverse=True)
        top = sims[: max(1, len(sims) // 3)]
        sim = sum(top) / len(top)
        # perfis reais ficam em ~0,10–0,35 contra vagas; 0,30 = nota cheia
        s.add("semantic", "Semelhança do texto do perfil com as vagas (TF-IDF, terço mais parecido)", min(1.0, sim / 0.30), 2,
              "Usar o vocabulário das vagas (mesmas palavras) ao descrever o que você fez.", 2, f"cosseno médio {sim:.2f}")
    bilingual = bool(p.get("about_en") or p.get("secondary_language_profile") or p.get("headline_en"))
    en_terms = sum(1 for w in ("engineer", "developer", "senior") if w in tk.norm(full))
    s.add("bilingual", "Encontrável em PT e EN (perfil secundário ou termos em inglês)", 1.0 if bilingual else min(1.0, en_terms / 3) * 0.6, 2,
          "Ter perfil secundário em inglês; recrutadores de fora buscam 'Senior Frontend Engineer'.", 2)
    cur_title = tk.norm((p.get("experience") or [{}])[0].get("title", ""))
    cur_ok = any(a and a in cur_title for a in aliases)
    s.add("title_match", "Título e cargo atual batem com a busca por cargo do recrutador",
          0.5 * has_title + 0.5 * cur_ok, 2, "Alinhar título e cargo atual ao nome do cargo-alvo.", 1)

    # ---------------- totais ----------------
    sec_out = {}
    overall_w = overall = 0.0
    for key, meta in rubric["sections"].items():
        sec = sections[key]
        tot = sec.total()
        sec_out[key] = {"label": meta["label"], "weight": meta["weight"], "score": tot, "items": sec.items}
        if tot is not None:
            overall += tot * meta["weight"]
            overall_w += meta["weight"]
    overall_score = round(overall / overall_w, 1) if overall_w else 0.0

    gaps = []
    for key, sec in sec_out.items():
        sw = rubric["sections"][key]["weight"]
        wsum = sum(i["weight"] for i in sec["items"] if i["score"] is not None) or 1
        for it in sec["items"]:
            if it["score"] is None or it["score"] >= 0.999:
                continue
            gain = sw * (it["weight"] / wsum) * (1 - it["score"]) * (100 / max(overall_w, 1))
            gaps.append({"section": key, "id": it["id"], "label": it["label"], "fix": it["fix"], "effort": it["effort"],
                         "gain": round(gain, 2), "priority": round(gain / it["effort"], 2), "detail": it["detail"]})
    gaps.sort(key=lambda g: -g["priority"])
    unverified = [f"{sec['label']}: {it['label']}" for sec in sec_out.values() for it in sec["items"] if it["score"] is None]

    return {
        "generated_at": today,
        "role": {"id": role["id"], "title_pt": role["title_pt"], "title_en": role["title_en"]},
        "n_jobs": kw.get("n_jobs"),
        "overall": overall_score,
        "sections": sec_out,
        "gaps": gaps,
        "unverified": unverified,
        "keywords": {"hit": hit_all, "missing": miss_all, "top": terms[:40], "semantic_similarity": sim},
        "metrics": p["metrics"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--keywords", required=True)
    ap.add_argument("--jobs")
    ap.add_argument("--rubric", default=str(RUBRIC))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = json.loads(Path(a.jobs).read_text())["jobs"] if a.jobs else None
    kw = json.loads(Path(a.keywords).read_text())
    if jobs:
        rid = kw["role"]["id"].split("-")[0]
        jobs = [j for j in jobs if j.get("role", "").startswith(rid)] or jobs
    rep = score(json.loads(Path(a.profile).read_text()), kw, json.loads(Path(a.rubric).read_text()), jobs)
    Path(a.out).write_text(json.dumps(rep, ensure_ascii=False, indent=2))
    print(f"Nota geral: {rep['overall']}/100  ({rep['role']['title_pt']})")
    for sec in rep["sections"].values():
        print(f"  {sec['label']:<45} {sec['score'] if sec['score'] is not None else '—':>6}")
    print("Top 8 ações:")
    for g in rep["gaps"][:8]:
        print(f"  +{g['gain']:>4} pts  esforço {g['effort']}  {g['fix'][:110]}")
    if rep["unverified"]:
        print(f"Não verificado ({len(rep['unverified'])}): " + "; ".join(rep["unverified"][:6]))


if __name__ == "__main__":
    main()
