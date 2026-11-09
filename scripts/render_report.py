#!/usr/bin/env python3
"""Gera a página do relatório (HTML para publicar como Artifact).

Uso:
  python3 render_report.py --report runs/D/report.json [--rewrites runs/D/rewrites.json] \
                           [--diff runs/D/diff.json] --out runs/D/report.html

rewrites.json (escrito pelo Claude depois da nota) — todos os campos opcionais:
{
  "profile_name": "...", "summary": "2–3 frases",
  "headline_current": "...",
  "headline_options": [{"pt": "...", "en": "...", "why": "..."}],
  "about_pt": "...", "about_en": "...",
  "experience": [{"company": "...", "title_current": "...", "title_suggested": "...",
                  "bullets_pt": ["..."], "bullets_en": ["..."]}],
  "skills_top5": ["..."], "skills_add": ["..."], "skills_remove": ["..."],
  "featured": ["..."],
  "recommendation_requests": [{"to": "Gestor atual", "message": "..."}],
  "content_plan": [{"when": "Semana 1", "idea": "..."}],
  "market_notes": [{"text": "...", "source": "...", "url": "..."}]
}
"""
from __future__ import annotations

import argparse
import json
from html import escape as e
from pathlib import Path

EFFORT = {1: "minutos", 2: "horas", 3: "semanas"}


def status(score):
    if score is None:
        return ("unknown", "?", "Não lido")
    if score >= 85:
        return ("good", "✓", "Forte")
    if score >= 65:
        return ("warn", "!", "Ajustar")
    if score >= 40:
        return ("serious", "!!", "Fraco")
    return ("critical", "✕", "Crítico")


def pill(score):
    cls, icon, label = status(score)
    return f'<span class="pill {cls}"><span aria-hidden="true">{icon}</span>{label}</span>'


def copy_block(text: str, label: str, cid: str) -> str:
    if not text:
        return ""
    return (f'<div class="copy"><div class="copy-head"><span class="eyebrow">{e(label)}</span>'
            f'<button type="button" class="btn" data-copy="{cid}">Copiar</button></div>'
            f'<pre id="{cid}" class="copytext">{e(text)}</pre></div>')


def section_bars(rep: dict) -> str:
    rows = []
    for key, sec in rep["sections"].items():
        sc = sec["score"]
        w = 0 if sc is None else sc
        rows.append(
            f'<div class="bar-row" data-tip="{e(sec["label"])}: {"—" if sc is None else f"{sc:.0f}/100"} · peso {sec["weight"]}%">'
            f'<div class="bar-label">{e(sec["label"])}<span class="muted"> · peso {sec["weight"]}</span></div>'
            f'<div class="bar-track" role="img" aria-label="{e(sec["label"])} {w:.0f} de 100">'
            f'<div class="bar-fill" style="width:{w:.1f}%"></div>'
            f'<div class="bar-goal" style="left:85%" title="meta 85"></div></div>'
            f'<div class="bar-val num">{"—" if sc is None else f"{sc:.0f}"}</div>'
            f'<div class="bar-pill">{pill(sc)}</div></div>')
    axis = "".join(f'<span style="left:{v}%">{v}</span>' for v in (0, 25, 50, 75, 100))
    return (f'<div class="bars">{"".join(rows)}<div class="bar-row axis-row"><div></div>'
            f'<div class="axis">{axis}</div><div></div><div></div></div></div>'
            '<p class="caption">Barra = nota da seção (0–100). Traço vertical = meta de 85 pontos. Peso = quanto a seção conta na nota geral.</p>')


def gaps_list(rep: dict, limit: int = 15) -> str:
    items = []
    for i, g in enumerate(rep["gaps"][:limit]):
        sec = rep["sections"][g["section"]]["label"]
        detail = f'<span class="muted"> — {e(g["detail"])}</span>' if g.get("detail") else ""
        items.append(
            f'<li class="gap"><label for="gap-{e(g["id"])}"><input type="checkbox" id="gap-{e(g["id"])}" data-key="{e(g["id"])}">'
            f'<span class="gap-body"><span class="gap-fix">{e(g["fix"])}</span>'
            f'<span class="gap-meta"><span class="tag">{e(sec)}</span><span class="tag">esforço: {EFFORT.get(g["effort"], g["effort"])}</span>{detail}</span></span>'
            f'<span class="gain num">+{g["gain"]:.1f}</span></label></li>')
    return f'<ol class="gaps">{"".join(items)}</ol>'


def keywords_block(rep: dict) -> str:
    hit = set(rep["keywords"]["hit"])
    rows = []
    for t in rep["keywords"]["top"][:30]:
        has = t["term"] in hit
        f = t["freq"] * 100
        br = "—" if t.get("freq_br") is None else f'{t["freq_br"] * 100:.0f}%'
        intl = "—" if t.get("freq_intl") is None else f'{t["freq_intl"] * 100:.0f}%'
        rows.append(
            f'<tr class="{"has" if has else "miss"}"><td>{e(t["term"])}{" <span class=\'tag\'>obrigatória</span>" if t["must"] else ""}</td>'
            f'<td class="kbar-cell" data-tip="{e(t["term"])}: {f:.0f}% das vagas (BR {br}, exterior {intl})">'
            f'<div class="kbar"><div class="kbar-fill {"on" if has else "off"}" style="width:{f:.0f}%"></div></div></td>'
            f'<td class="num">{f:.0f}%</td><td class="num muted">{br}</td><td class="num muted">{intl}</td>'
            f'<td>{"<span class=\'pill good\'><span aria-hidden=\'true\'>✓</span>No perfil</span>" if has else "<span class=\'pill critical\'><span aria-hidden=\'true\'>✕</span>Falta</span>"}</td></tr>')
    sim = rep["keywords"].get("semantic_similarity")
    sim_txt = f'Semelhança do texto do perfil com as vagas (TF-IDF): <b class="num">{sim:.2f}</b> (0,30 ou mais é bom). ' if sim is not None else ""
    return (f'<p>{sim_txt}Baseado em <b>{rep.get("n_jobs") or 0}</b> vagas reais coletadas em {e(rep["generated_at"])}. '
            'Barra cheia = termo que você já tem; barra vazada = termo que falta.</p>'
            '<div class="table-wrap"><table class="kw"><thead><tr><th>Palavra-chave</th><th>Vagas que pedem</th><th class="num">Total</th>'
            '<th class="num">BR</th><th class="num">Exterior</th><th>Seu perfil</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def details_block(rep: dict) -> str:
    out = []
    for sec in rep["sections"].values():
        rows = []
        for it in sec["items"]:
            sc = None if it["score"] is None else it["score"] * 100
            rows.append(f'<tr><td>{e(it["label"])}{"<div class=muted>" + e(it["detail"]) + "</div>" if it.get("detail") else ""}</td>'
                        f'<td class="num">{"—" if sc is None else f"{sc:.0f}"}</td><td>{pill(sc)}</td></tr>')
        sc = sec["score"]
        out.append(f'<details><summary><span>{e(sec["label"])}</span><span class="num">{"—" if sc is None else f"{sc:.0f}"}</span>{pill(sc)}</summary>'
                   f'<div class="table-wrap"><table><thead><tr><th>Critério</th><th class="num">Nota</th><th>Situação</th></tr></thead>'
                   f'<tbody>{"".join(rows)}</tbody></table></div></details>')
    return "".join(out)


def search_card(name: str, headline: str, label: str, location: str | None) -> str:
    cut = 120
    shown = headline if len(headline) <= cut else headline[:cut].rstrip() + "…"
    initials = "".join(w[0] for w in (name or "?").split()[:2]).upper()
    return (f'<figure class="card"><figcaption class="eyebrow">{e(label)}</figcaption>'
            f'<div class="card-row"><div class="avatar" aria-hidden="true">{e(initials)}</div>'
            f'<div class="card-text"><div class="card-name">{e(name or "Seu nome")}</div>'
            f'<div class="card-head">{e(shown)}</div><div class="muted">{e(location or "")}</div></div></div></figure>')


def rewrites_block(rw: dict) -> str:
    parts = []
    hs = rw.get("headline_options") or []
    if hs:
        cards = []
        for i, h in enumerate(hs):
            cards.append(f'<div class="opt"><div class="eyebrow">Opção {i + 1}</div>'
                         f'{copy_block(h.get("pt", ""), "Português", f"h{i}pt")}{copy_block(h.get("en", ""), "Inglês (perfil secundário)", f"h{i}en")}'
                         f'{"<p class=muted>" + e(h["why"]) + "</p>" if h.get("why") else ""}</div>')
        parts.append(f'<h3>Título</h3><div class="opts">{"".join(cards)}</div>')
    if rw.get("about_pt") or rw.get("about_en"):
        parts.append('<h3>Sobre</h3><div class="two">' + copy_block(rw.get("about_pt", ""), "Português", "about-pt")
                     + copy_block(rw.get("about_en", ""), "Inglês (perfil secundário)", "about-en") + "</div>")
    for i, x in enumerate(rw.get("experience") or []):
        title = ""
        if x.get("title_suggested"):
            title = f'<p>Cargo: <s class="muted">{e(x.get("title_current", ""))}</s> → <b>{e(x["title_suggested"])}</b></p>'
        parts.append(f'<h3>Experiência · {e(x.get("company", ""))}</h3>{title}<div class="two">'
                     + copy_block("\n".join("• " + b for b in x.get("bullets_pt") or []), "Tópicos em português", f"x{i}pt")
                     + copy_block("\n".join("• " + b for b in x.get("bullets_en") or []), "Tópicos em inglês", f"x{i}en") + "</div>")
    if rw.get("skills_top5") or rw.get("skills_add"):
        chips = lambda xs, cls: "".join(f'<span class="chip {cls}">{e(s)}</span>' for s in xs)  # noqa: E731
        parts.append('<h3>Competências</h3>'
                     + (f'<p class="eyebrow">Fixar como principais (nesta ordem)</p><div class="chips">{chips(rw.get("skills_top5") or [], "top")}</div>' if rw.get("skills_top5") else "")
                     + (f'<p class="eyebrow">Adicionar (só se você realmente usa)</p><div class="chips">{chips(rw.get("skills_add") or [], "")}</div>' if rw.get("skills_add") else "")
                     + (f'<p class="eyebrow">Remover ou descer na lista</p><div class="chips">{chips(rw.get("skills_remove") or [], "off")}</div>' if rw.get("skills_remove") else ""))
    if rw.get("featured"):
        parts.append("<h3>Destaques</h3><ul>" + "".join(f"<li>{e(f)}</li>" for f in rw["featured"]) + "</ul>")
    reqs = rw.get("recommendation_requests") or []
    if reqs:
        parts.append("<h3>Pedidos de recomendação prontos</h3><div class='two'>"
                     + "".join(copy_block(r.get("message", ""), "Para: " + r.get("to", ""), f"rec{i}") for i, r in enumerate(reqs)) + "</div>")
    plan = rw.get("content_plan") or []
    if plan:
        parts.append('<h3>Plano de conteúdo — 30 dias</h3><ol class="plan">'
                     + "".join(f'<li><span class="eyebrow">{e(p.get("when", ""))}</span>{e(p.get("idea", ""))}</li>' for p in plan) + "</ol>")
    return "".join(parts)


def market_block(rw: dict) -> str:
    notes = rw.get("market_notes") or []
    if not notes:
        return ""
    li = []
    for n in notes:
        src = f' <a href="{e(n["url"])}" target="_blank" rel="noopener">{e(n.get("source") or "fonte")}</a>' if n.get("url") else (f' <span class="muted">({e(n["source"])})</span>' if n.get("source") else "")
        li.append(f"<li>{e(n['text'])}{src}</li>")
    return f'<ul class="market">{"".join(li)}</ul>'


def diff_block(d: dict | None) -> str:
    if not d:
        return '<p class="muted">Primeira rodada. Rode a auditoria de novo depois das mudanças para ver a evolução aqui.</p>'
    rows = "".join(f'<tr><td>{e(s["label"])}</td><td class="num">{s["before"] if s["before"] is not None else "—"}</td>'
                   f'<td class="num">{s["after"] if s["after"] is not None else "—"}</td>'
                   f'<td class="num">{"" if s["delta"] is None else f"{s["delta"]:+.0f}"}</td></tr>' for s in d["sections"].values())
    return (f'<p>{e(d["before_date"])} → {e(d["after_date"])}: <b class="num">{d["overall_before"]} → {d["overall_after"]} ({d["overall_delta"]:+})</b></p>'
            f'<div class="table-wrap"><table><thead><tr><th>Seção</th><th class="num">Antes</th><th class="num">Agora</th><th class="num">Δ</th></tr></thead><tbody>{rows}</tbody></table></div>')


CSS = r"""
/* Layout: coluna única de leitura (~72ch) com faixas de seção; cartões só no simulador de busca e nos textos para copiar */
:root{
  --bg:#f6f7f6; --surface:#fdfdfc; --ink:#141816; --ink-2:#4b5550; --muted:#6c7671; --line:#d9dedb;
  --accent:#1f6f5c; --accent-soft:#d5ebe3; --accent-ink:#ffffff;
  --good:#0ca30c; --warn:#fab219; --serious:#ec835a; --critical:#d03b3b;
  --f-display:"Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --f-body:"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --f-mono:"IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121514; --surface:#1a1e1c; --ink:#eef1ef; --ink-2:#b9c2bd; --muted:#8f9a94; --line:#2d3431;
  --accent:#4fb79a; --accent-soft:#1d3a31; --accent-ink:#0d1210; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121514; --surface:#1a1e1c; --ink:#eef1ef; --ink-2:#b9c2bd; --muted:#8f9a94; --line:#2d3431;
  --accent:#4fb79a; --accent-soft:#1d3a31; --accent-ink:#0d1210; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:16px/1.6 var(--f-body);
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:980px;margin:0 auto;padding-block:40px 80px;display:grid;gap:56px}
h1,h2,h3{font-family:var(--f-display);text-wrap:balance;line-height:1.15;margin:0}
h1{font-size:clamp(28px,5vw,44px);font-weight:700;letter-spacing:-.02em}
h2{font-size:26px;font-weight:650;letter-spacing:-.01em}
h3{font-size:19px;font-weight:600;margin-top:28px}
p{margin:0;max-width:72ch} section{display:grid;gap:16px;min-width:0}
a{color:var(--accent)} .muted{color:var(--muted)}
.eyebrow{font:600 12px/1.4 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
.num{font-variant-numeric:tabular-nums;font-family:var(--f-mono)}
.hero{display:grid;grid-template-columns:auto 1fr;gap:32px;align-items:center}
.score{width:168px;height:168px;position:relative}
.score svg{width:100%;height:100%;transform:rotate(-90deg)}
.score .v{position:absolute;inset:0;display:grid;place-content:center;text-align:center}
.score .v b{font:700 52px/1 var(--f-display)} .score .v span{font:12px var(--f-mono);color:var(--muted)}
.hero-text{display:grid;gap:12px;min-width:0}
.note{font-size:14px;color:var(--ink-2);border-left:3px solid var(--line);padding-left:12px}
.pill{display:inline-flex;gap:6px;align-items:center;font:600 12px/1 var(--f-body);padding:4px 9px;border-radius:99px;white-space:nowrap;
  border:1px solid currentColor;color:var(--ink)}
.pill.good span{color:var(--good)} .pill.warn span{color:var(--warn)} .pill.serious span{color:var(--serious)} .pill.critical span{color:var(--critical)} .pill.unknown{color:var(--muted)}
.pill span{font-weight:800}
.bars{display:grid;gap:10px}
.bar-row{display:grid;grid-template-columns:minmax(0,15rem) minmax(0,1fr) 3rem 6.5rem;gap:12px;align-items:center}
.bar-label{font-size:14px;min-width:0}
.bar-track{position:relative;height:14px;background:var(--line);border-radius:4px;overflow:visible}
.bar-fill{height:100%;background:var(--accent);border-radius:4px}
.bar-goal{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--ink-2)}
.bar-val{text-align:right;font-size:15px}
.axis{position:relative;height:16px;font:11px var(--f-mono);color:var(--muted)}
.axis span{position:absolute;transform:translateX(-50%)}
.caption{font-size:13px;color:var(--muted)}
.gaps{list-style:none;padding:0;margin:0;display:grid;border-top:1px solid var(--line)}
.gap label{display:grid;grid-template-columns:auto 1fr auto;gap:14px;align-items:start;padding:14px 4px;border-bottom:1px solid var(--line);cursor:pointer}
.gap input{width:18px;height:18px;margin-top:3px;accent-color:var(--accent)}
.gap input:checked ~ .gap-body .gap-fix{text-decoration:line-through;color:var(--muted)}
.gap-body{display:grid;gap:6px;min-width:0} .gap-meta{display:flex;flex-wrap:wrap;gap:6px;font-size:13px}
.gain{font-size:15px;color:var(--accent);font-weight:600}
.tag{font:12px/1 var(--f-mono);padding:4px 7px;border-radius:4px;background:var(--accent-soft);color:var(--ink)}
.table-wrap{overflow-x:auto;min-width:0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
th{font:600 12px var(--f-mono);text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2)}
th.num,td.num{text-align:right}
.kbar-cell{width:34%;min-width:120px}
.kbar{height:10px;border-radius:3px;background:transparent}
.kbar-fill{height:100%;border-radius:3px}
.kbar-fill.on{background:var(--accent)}
.kbar-fill.off{background:repeating-linear-gradient(135deg,transparent 0 4px,var(--accent-soft) 4px 7px);border:1.5px solid var(--accent)}
tr.miss td:first-child{font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:16px}
.card{margin:0;padding:16px;background:var(--surface);border:1px solid var(--line);border-radius:10px;display:grid;gap:12px}
.card-row{display:flex;gap:12px;min-width:0} .card-text{min-width:0}
.avatar{flex:none;width:48px;height:48px;border-radius:50%;display:grid;place-content:center;background:var(--accent-soft);font:700 16px var(--f-display)}
.card-name{font-weight:600} .card-head{font-size:14px;line-height:1.45}
.opts{display:grid;gap:20px}
.opt{display:grid;gap:10px;padding-bottom:20px;border-bottom:1px solid var(--line)}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px}
.copy{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-width:0;display:grid;gap:8px}
.copy-head{display:flex;justify-content:space-between;align-items:center;gap:8px}
.copytext{margin:0;white-space:pre-wrap;word-wrap:break-word;font:14px/1.55 var(--f-body);color:var(--ink)}
.btn{font:600 13px var(--f-body);padding:6px 12px;border-radius:6px;border:1px solid var(--accent);background:var(--accent);color:var(--accent-ink);cursor:pointer}
.btn:focus-visible,summary:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{font:13px/1 var(--f-body);padding:7px 11px;border-radius:99px;border:1px solid var(--line);background:var(--surface)}
.chip.top{border-color:var(--accent);font-weight:600} .chip.off{text-decoration:line-through;color:var(--muted)}
details{border-bottom:1px solid var(--line)}
summary{display:grid;grid-template-columns:1fr auto auto;gap:12px;align-items:center;padding:12px 4px;cursor:pointer;font-weight:600}
.plan,.market{display:grid;gap:10px;padding-left:20px;margin:0}
.plan li{display:grid;gap:2px}
.tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--bg);font:13px var(--f-body);padding:6px 9px;border-radius:6px;z-index:5;max-width:280px}
@media (max-width:640px){
  .hero{grid-template-columns:1fr}
  .bar-row{grid-template-columns:1fr 2.5rem;row-gap:4px}
  .bar-label{grid-column:1/-1} .bar-pill{display:none} .axis-row{display:none}
}
@media (prefers-reduced-motion:no-preference){.bar-fill{transition:width .6s ease}}
"""

JS = r"""
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{
  const el=document.getElementById(b.dataset.copy);const t=el.innerText;
  const done=()=>{b.textContent='Copiado';setTimeout(()=>b.textContent='Copiar',1600)};
  const sel=()=>{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selecionado — use Ctrl/Cmd+C'};
  try{navigator.clipboard.writeText(t).then(done,sel)}catch(_){sel()}
}));
const KEY='li-audit-done-'+document.body.dataset.run;
let done={};try{done=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(_){}
document.querySelectorAll('.gap input').forEach(c=>{c.checked=!!done[c.dataset.key];c.addEventListener('change',()=>{done[c.dataset.key]=c.checked;try{localStorage.setItem(KEY,JSON.stringify(done))}catch(_){}})});
const tip=document.createElement('div');tip.className='tip';tip.hidden=true;document.body.appendChild(tip);
document.querySelectorAll('[data-tip]').forEach(el=>{
  el.addEventListener('mousemove',ev=>{tip.textContent=el.dataset.tip;tip.hidden=false;tip.style.left=Math.min(ev.clientX+14,innerWidth-290)+'px';tip.style.top=(ev.clientY+14)+'px'});
  el.addEventListener('mouseleave',()=>tip.hidden=true);
});
"""


def render(rep: dict, rw: dict, d: dict | None) -> str:
    overall = rep["overall"]
    circ = 2 * 3.14159 * 70
    ring = (f'<div class="score" role="img" aria-label="Nota geral {overall:.0f} de 100"><svg viewBox="0 0 160 160">'
            f'<circle cx="80" cy="80" r="70" fill="none" stroke="var(--line)" stroke-width="12"/>'
            f'<circle cx="80" cy="80" r="70" fill="none" stroke="var(--accent)" stroke-width="12" stroke-linecap="round" '
            f'stroke-dasharray="{circ * overall / 100:.1f} {circ:.1f}"/></svg>'
            f'<div class="v"><b class="num">{overall:.0f}</b><span>de 100</span></div></div>')
    name = rw.get("profile_name") or ""
    role = rep["role"]
    head_now = rw.get("headline_current") or ""
    best = (rw.get("headline_options") or [{}])[0]
    cards = ""
    if head_now or best:
        cards = ('<section><h2>Como um recrutador te vê na lista de resultados</h2>'
                 '<p>Na lista de busca aparecem nome, título (cortado por volta de 120 caracteres) e local. É isso que decide o clique.</p><div class="cards">'
                 + search_card(name, head_now, "Hoje", None)
                 + (search_card(name, best.get("pt", ""), "Com o título sugerido", None) if best.get("pt") else "")
                 + "</div></section>")
    unverified = rep.get("unverified") or []
    unv = ("<section><h2>O que não deu para ler</h2><p>Esses critérios ficaram fora da nota (não contam nem contra nem a favor). "
           "Confira você mesmo:</p><ul>" + "".join(f"<li>{e(u)}</li>" for u in unverified) + "</ul></section>") if unverified else ""
    rewrites = rewrites_block(rw)
    market = market_block(rw)
    return f"""<title>Auditoria LinkedIn {e(name)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main data-run="{e(rep['generated_at'])}">
<header class="hero">{ring}<div class="hero-text">
  <span class="eyebrow">Auditoria de perfil · {e(rep['generated_at'])} · cargo-alvo: {e(role['title_pt'])} / {e(role['title_en'])}</span>
  <h1>{e(name) + ', seu' if name else 'Seu'} perfil está em {overall:.0f} de 100</h1>
  {"<p>" + e(rw["summary"]) + "</p>" if rw.get("summary") else ""}
  <p class="note">100 aqui significa cumprir toda a rubrica, montada com fontes de 2026 sobre como o LinkedIn Recruiter, o Hiring Assistant e os ATS leem perfis. Não garante entrevista; aumenta as chances de você aparecer e ser chamado.</p>
</div></header>
<section><h2>Nota por seção</h2>{section_bars(rep)}</section>
<section><h2>O que fazer primeiro</h2><p>Ordenado por pontos ganhos ÷ esforço. Marque o que já fez; a marcação fica salva neste navegador.</p>{gaps_list(rep)}</section>
{cards}
<section><h2>Palavras-chave que as vagas pedem</h2>{keywords_block(rep)}</section>
{"<section><h2>Textos prontos para colar</h2><p>Onde aparece [X], troque pelo seu número real. Nada foi inventado: sem o número, o tópico fica sem ele.</p>" + rewrites + "</section>" if rewrites else ""}
{"<section><h2>O que o mercado olha hoje</h2>" + market + "</section>" if market else ""}
<section><h2>Detalhe de cada critério</h2>{details_block(rep)}</section>
<section><h2>Evolução</h2>{diff_block(d)}</section>
{unv}
</main>
<script>document.body.dataset.run={json.dumps(rep['generated_at'])};{JS}</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", required=True)
    ap.add_argument("--rewrites")
    ap.add_argument("--diff")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rep = json.loads(Path(a.report).read_text())
    rw = json.loads(Path(a.rewrites).read_text()) if a.rewrites else {}
    d = json.loads(Path(a.diff).read_text()) if a.diff else None
    Path(a.out).write_text(render(rep, rw, d))
    print(f"página -> {a.out}")


if __name__ == "__main__":
    main()
