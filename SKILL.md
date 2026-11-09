---
name: linkedin-audit
description: Auditoria completa de perfil do LinkedIn para qualquer cargo (padrão Desenvolvedor Frontend Sênior; também fullstack ou cargo livre). Lê o perfil logado pelo Claude in Chrome, pesquisa o que recrutadores e motores de busca com IA (LinkedIn Recruiter AI Search, Hiring Assistant, Gupy, Greenhouse, Juicebox…) olham hoje, coleta vagas reais, dá nota 0–100 por seção com Python, reescreve título/Sobre/experiências em PT e EN e entrega página (Artifact) + documento editável + comparação com a rodada anterior. Use quando o usuário pedir análise, nota, auditoria, revisão ou melhoria do perfil do LinkedIn, palavras-chave para recrutador, "como aparecer mais para recrutadores", ou quiser medir a evolução do perfil.
---

# Auditoria de perfil LinkedIn

Pasta das rodadas: `~/Documents/linkedin-audit/runs/AAAA-MM-DD/`. Scripts em `scripts/` (só biblioteca padrão do Python 3.12+).
Escreva tudo para o usuário em português simples.

## 0. Preparar
- Cargo-alvo: `references/roles/<id>.json` (`frontend-senior`, `fullstack`). Outro cargo: copie um arquivo de role e ajuste `title_*`, `title_aliases`, `must`, `nice`, ou rode com `--role-title "Cargo"` (as palavras-chave saem só das vagas).
- Crie a pasta da rodada com a data de hoje.

## 1. Pesquisa em paralelo (agents em background, enquanto lê o perfil)
- **Mercado**: se `references/market-2026.md` tiver mais de ~3 meses, lance um agent general-purpose para atualizá-lo (WebSearch extended; fontes marcadas [OFICIAL]/[BLOG]/sem fonte; nunca inventar números). Atualize os pesos em `references/rubric.json` se a pesquisa sugerir outros (os pesos devem somar 100).
- **Vagas**: lance um agent para coletar ~40 vagas reais do cargo (BR em PT + exterior em EN) em boards públicos (Gupy, Greenhouse, Lever, Ashby, Programathor, Remotar, Wellfound). O LinkedIn Jobs bloqueia. Formato: `{"collected_at":..., "jobs":[{"role","market":"br|intl","lang","title","company","url","text"}]}` → `jobs.json`.

## 2. Ler o perfil (Claude in Chrome, só leitura)
Carregue a skill `chrome-browser`. Se as ferramentas `mcp__claude-in-chrome__*` não existirem, peça ao usuário para rodar `/chrome` (ou `claude --chrome`) e conectar a extensão; não tente outro caminho sem perguntar. Abra uma aba nova e leia com `get_page_text`/`read_page`:
`linkedin.com/in/me/` (topo: nome, título, local, foto/banner, Open to Work, verificado), `/details/experience/`, `/details/skills/` (endossos, quais estão fixadas como principais), `/details/recommendations/`, `/details/certifications/`, `/details/projects/`, `/details/languages/`, `/details/education/`, Destaques, Apps conectados, informações de contato (`/overlay/contact-info/`), `/recent-activity/all/` (posts e comentários dos últimos 90 dias), `linkedin.com/dashboard/` e `/analytics/search-appearances/` (visualizações, aparições em buscas, quem buscou), `linkedin.com/sales/ssi` (SSI).
Monte o `profile.json` no formato de `scripts/profile_schema.py` (rode o script sem argumentos para ver o modelo). **Campo não lido = null** (não pune). Nunca edite nada no LinkedIn sem o usuário pedir.
Valide: `python3 scripts/profile_schema.py runs/D/profile.json`.

## 3. Nota
```
python3 scripts/keywords.py --jobs runs/D/jobs.json --role frontend-senior --out runs/D/keywords.json
python3 scripts/score.py --profile runs/D/profile.json --keywords runs/D/keywords.json --jobs runs/D/jobs.json --out runs/D/report.json
python3 scripts/diff_runs.py --latest ~/Documents/linkedin-audit/runs --out runs/D/diff.json   # se houver rodada anterior
```
Revise `keywords.json → unmapped`: termos frequentes fora do dicionário. Se forem relevantes, adicione-os a `extra_terms` do role (ou ao `SYNONYMS` em `textkit.py`) e rode de novo.

## 4. Reescrita (`rewrites.json`, formato no topo de `render_report.py`)
- Use só fatos do perfil. Números que você não sabe viram `[X]`, nunca um número inventado.
- Título: 3 opções, PT e EN, até 220 caracteres, nesta ordem: cargo canônico | stack top 3–4 | resultado/proposta de valor.
- Sobre PT e EN: cargo e anos nas 2 primeiras linhas, 2–3 resultados com número, linha "Stack:", chamada para contato.
- Experiências recentes: tópicos com verbo + o que fez + resultado; cargo atual com nome de mercado.
- Competências: top 5 a fixar, o que adicionar (só o que a pessoa usa), o que remover.
- Destaques, 3 pedidos de recomendação prontos e plano de conteúdo de 30 dias.
- `market_notes`: 6–8 pontos de `market-2026.md` com fonte e URL.

## 5. Entregar
1. `python3 scripts/render_report.py --report ... --rewrites ... [--diff ...] --out runs/D/report.html`. Publique com a ferramenta Artifact (icon `chart`). Na próxima rodada, use a mesma URL (`url`) para manter o link.
2. Documento editável no Claude Docs (carregue a skill `docs`) com o diagnóstico e todos os textos novos.
3. Responda no chat com: nota geral, 3 ações de maior ganho e os links.

## Testes
`python3 -m unittest discover -s ~/.claude/skills/linkedin-audit/tests`
