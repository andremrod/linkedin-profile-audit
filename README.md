# LinkedIn Profile Audit

[![tests](https://github.com/andremrod/linkedin-profile-audit/actions/workflows/tests.yml/badge.svg)](https://github.com/andremrod/linkedin-profile-audit/actions/workflows/tests.yml)

Scores a LinkedIn profile from 0 to 100 against **real job postings** and **how recruiter search works in 2026**: LinkedIn Recruiter AI search, Hiring Assistant and ATS ranking such as Gupy. It then lists the changes that gain the most points for the least effort.

- **Any role.** Ships with *Senior Front-end* and *Full Stack*. For any other role, pass a title and the keywords come from the job postings.
- **Python standard library only.** No `pip install`. Keyword matching uses synonyms (`React.js` → `react`). Semantic similarity is a hand-written TF-IDF + cosine, a small stand-in for embedding-based search.
- **Honest scoring.** A field you could not read is `null`. It is left out of the score and listed as *not verified*, so it neither costs nor earns points. Missing numbers in rewritten texts become `[X]` and are never invented.
- **Tracks progress.** Compare two runs to see which sections went up and which keywords you gained.
- **Works as a Claude Code skill.** Claude reads your profile in your own browser, collects postings, runs the scripts and rewrites your headline, About and experience in PT and EN.

> The report and suggestions are in **Brazilian Portuguese**. The target market is Brazil plus international roles.

## Quick start

Requires Python 3.12+.

```bash
git clone https://github.com/andremrod/linkedin-profile-audit.git
cd linkedin-profile-audit
python3 audit.py --example        # runs with a fictional profile from examples/
open runs/example/report.html     # macOS; on Linux use xdg-open
```

Output:

```
Nota geral: 16.3/100  (Desenvolvedor Frontend Sênior)
  Visibilidade na busca                           24.8
  Experiência                                     25.9
  Competências                                     3.7
  ...
Top 8 ações:
  +5.23 pts  esforço 1  Adicionar como competência: react, typescript, acessibilidade, design system, next.js…
  +4.41 pts  esforço 1  Começar o título por 'Desenvolvedor Frontend Sênior' ou 'Senior Frontend Engineer'.
```

## Auditing your own profile

1. **Describe your profile** in a `profile.json`. Print the template with:
   ```bash
   python3 scripts/profile_schema.py                 # prints the template
   python3 scripts/profile_schema.py my/profile.json # validates your file
   ```
   Fill in what you can see on your profile: headline, About, each experience, skills with endorsements, recommendations, Open to Work, posts in the last 90 days, and so on. Leave anything you did not check as `null`.

2. **Collect job postings** for the role you want in a `jobs.json`. Around 40 is a good number, from Brazilian and international boards. [`examples/jobs.json`](examples/jobs.json) shows the format:
   ```json
   {"collected_at": "2026-11-09", "jobs": [
     {"role": "frontend", "market": "br", "lang": "pt", "title": "...", "company": "...", "url": "...", "text": "full posting text"}
   ]}
   ```

3. **Run the audit**:
   ```bash
   python3 audit.py --profile my/profile.json --jobs my/jobs.json --role frontend-senior
   python3 audit.py --profile my/profile.json --jobs my/jobs.json --role fullstack
   python3 audit.py --profile my/profile.json --jobs my/jobs.json --role-title "Data Engineer"
   ```
   Each run goes to `runs/YYYY-MM-DD/` and contains `keywords.json`, `report.json` and `report.html`.

4. **Optional:** to show rewritten texts in the page, pass `--rewrites rewrites.json`. Its format is documented at the top of [`scripts/render_report.py`](scripts/render_report.py). To show progress since a previous run, pass `--previous runs/<earlier-date>`.

`runs/` is in `.gitignore` because it holds personal data.

## Using it as a Claude Code skill

This repository is also a [Claude Code](https://claude.com/claude-code) skill. [`SKILL.md`](SKILL.md) defines the workflow.

```bash
git clone https://github.com/andremrod/linkedin-profile-audit.git ~/.claude/skills/linkedin-audit
```

Then ask Claude Code something like *"audite meu perfil do LinkedIn para Desenvolvedor Frontend Sênior"*. With the [Claude in Chrome](https://claude.com/chrome) extension connected, Claude does the following:

1. Reads your logged-in profile in a new tab. This is read-only: nothing on LinkedIn is changed.
2. Researches the market and collects about 40 real postings, with background agents running in parallel.
3. Runs the scripts.
4. Writes 3 headline options, a new About, experience bullets in PT and EN, the skills to pin, recommendation requests and a 30-day content plan.
5. Delivers the report page and an editable document.

## How the score works

The section weights are in [`references/rubric.json`](references/rubric.json) and add up to 100. The reasons behind them, with sources, are in [`references/market-2026.md`](references/market-2026.md).

| Section | Weight | What it checks |
|---|---|---|
| Search visibility | 25 | Headline starts with the canonical title and holds 3+ in-demand keywords (≤220 chars); photo, banner, location, custom URL, verification, Open to Work visible to recruiters only |
| Experience | 20 | Current title uses the market name, bullets with metrics, keywords from the postings, skills linked to each role, no unexplained gaps over 6 months, education |
| Skills | 15 | Coverage of the keywords from the postings, ~50 skills, top 5 pinned and in demand, endorsements |
| AI search | 15 | Weighted coverage of the top 40 keywords across the whole profile, all must-have terms present, findable in PT and EN, TF-IDF cosine between the profile and the postings, title matches recruiter title search |
| About | 10 | Title and years in the first lines, measured results, a "Stack:" line, a call to action, English version |
| Social proof | 10 | Recent recommendations, certifications, featured items, projects, portfolio/GitHub links, languages, connected apps |
| Activity | 5 | Posts and comments in the last 90 days, connections |

Each criterion scores from 0 to 1. Every gap gets an **estimated gain** in points and an **effort** level (minutes, hours or weeks). The list is sorted by gain ÷ effort, so the quickest wins come first.

**What the score is not:** LinkedIn does not publish its ranking weights. This is a rubric built from official documentation and the job postings you collected. It does not guarantee interviews.

## Project layout

```
audit.py                    one command: keywords → score → diff → HTML
scripts/
  profile_schema.py         profile.json template and validation
  keywords.py               keywords weighted by frequency in the postings (PT + EN, synonyms)
  textkit.py                synonym dictionary, longest-match term finder, TF-IDF/cosine
  score.py                  0–100 score per section + gaps ranked by gain ÷ effort
  diff_runs.py              progress between two runs
  render_report.py          report.json → self-contained HTML page
references/
  rubric.json               section weights and thresholds
  roles/*.json              seed keywords per role (must / nice / title aliases)
  market-2026.md            research: how recruiters and AI tools find profiles (with sources)
tests/                      unittest + fictional fixtures
examples/                   fictional profile, postings and rewrites
SKILL.md                    Claude Code skill workflow
```

**Adding a role:** copy `references/roles/frontend-senior.json`, change `title_pt`, `title_en`, `title_aliases`, `must` and `nice`, then pass its id to `--role`.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

CI runs the tests and the end-to-end example on Python 3.12 and 3.13.

<details>
<summary><strong>Em português</strong></summary>

**O que é:** uma ferramenta que dá nota de 0 a 100 ao seu perfil do LinkedIn. A nota compara o perfil com vagas reais do cargo que você quer e com o que a busca de recrutadores usa em 2026: busca com IA do LinkedIn Recruiter, Hiring Assistant e ranking de ATS como a Gupy. Ela mostra, em ordem, as mudanças que dão mais pontos com menos esforço. Funciona para qualquer cargo e usa só Python, sem instalar nada.

**Como rodar:**

```bash
python3 audit.py --example                                   # exemplo com perfil fictício
python3 audit.py --profile perfil.json --jobs vagas.json --role frontend-senior
python3 audit.py --profile perfil.json --jobs vagas.json --role-title "Analista de Dados"
```

Veja o modelo do `perfil.json` com `python3 scripts/profile_schema.py`. O resultado fica em `runs/AAAA-MM-DD/report.html`.

**Com o Claude Code:** clone em `~/.claude/skills/linkedin-audit` e peça *"audite meu perfil do LinkedIn"*. O Claude lê o perfil no seu navegador, sem alterar nada, junta as vagas, calcula a nota e reescreve título, Sobre e experiências em PT e EN.

Campo não lido não tira ponto. Número que não se sabe vira `[X]`, nunca é inventado. A nota é uma rubrica baseada em fontes, não uma garantia de entrevista.

</details>

## License

[MIT](LICENSE)
