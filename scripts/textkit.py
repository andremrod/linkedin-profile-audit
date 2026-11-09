"""Ferramentas de texto: normalização PT/EN, sinônimos de termos técnicos e TF-IDF.

Só biblioteca padrão. Os termos canônicos estão em português quando o termo é
comportamental ("mentoria") e no nome oficial quando é tecnologia ("next.js").
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

# canônico -> variações (minúsculas, sem acento). A busca é por fronteira de palavra.
SYNONYMS: dict[str, list[str]] = {
    # linguagens / web
    "javascript": ["javascript", "js", "ecmascript", "es6", "es2015"],
    "typescript": ["typescript", "ts"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss", "less", "css-in-js", "styled-components", "styled components"],
    "python": ["python"],
    "java": ["java"],
    "go": ["golang", "go lang", "go (golang)"],
    "c#": ["c#", ".net", "dotnet", "asp.net"],
    "php": ["php", "laravel"],
    "ruby": ["ruby", "rails", "ruby on rails"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    # frameworks frontend
    "react": ["react", "reactjs", "react.js", "react js", "react hooks", "hooks"],
    "next.js": ["next.js", "nextjs", "next js", "app router"],
    "vue": ["vue", "vuejs", "vue.js", "nuxt", "nuxt.js"],
    "angular": ["angular", "angularjs", "rxjs"],
    "svelte": ["svelte", "sveltekit"],
    "react native": ["react native", "react-native", "expo"],
    "remix": ["remix"],
    "redux": ["redux", "redux toolkit", "rtk"],
    "zustand": ["zustand", "jotai", "recoil", "mobx"],
    "react query": ["react query", "tanstack query", "tanstack", "swr"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "design system": ["design system", "design systems", "biblioteca de componentes", "component library", "ui kit", "storybook"],
    "storybook": ["storybook"],
    "web components": ["web components", "lit element", "stencil"],
    "micro frontends": ["micro frontends", "micro-frontends", "microfrontends", "micro frontend", "module federation"],
    "vite": ["vite"],
    "webpack": ["webpack", "rollup", "esbuild", "turbopack", "babel"],
    "ssr": ["ssr", "server side rendering", "server-side rendering", "ssg", "isr", "server components", "rsc"],
    "pwa": ["pwa", "progressive web app", "service worker", "service workers"],
    "graphql": ["graphql", "apollo", "relay"],
    "rest api": ["restful", "rest api", "api rest", "apis rest", "apis restful", "rest apis"],
    "websockets": ["websocket", "websockets", "socket.io"],
    # qualidade
    "testes automatizados": ["testes automatizados", "testes unitarios", "testes de integracao", "unit tests", "unit testing",
                              "automated tests", "automated testing", "integration tests", "e2e", "end-to-end", "testes e2e"],
    "jest": ["jest", "vitest"],
    "testing library": ["testing library", "react testing library"],
    "cypress": ["cypress"],
    "playwright": ["playwright"],
    "tdd": ["tdd", "test driven development", "test-driven"],
    "clean code": ["clean code", "codigo limpo", "solid"],
    "code review": ["code review", "code reviews", "revisao de codigo", "pull requests"],
    # performance / web
    "performance web": ["performance", "web performance", "otimizacao de performance", "lighthouse", "lazy loading", "code splitting"],
    "core web vitals": ["core web vitals", "web vitals", "lcp", "cls", "inp"],
    "acessibilidade": ["acessibilidade", "accessibility", "a11y", "wcag", "aria"],
    "seo": ["seo"],
    "responsivo": ["responsivo", "responsive", "mobile first", "mobile-first"],
    "i18n": ["i18n", "internacionalizacao", "internationalization"],
    # backend
    "node.js": ["node", "node.js", "nodejs", "node js"],
    "nestjs": ["nestjs", "nest.js"],
    "express": ["express", "express.js", "fastify"],
    "sql": ["sql", "banco de dados relacional", "relational databases"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql", "mariadb"],
    "mongodb": ["mongodb", "mongo", "mongoose"],
    "redis": ["redis"],
    "prisma": ["prisma", "typeorm", "drizzle", "sequelize"],
    "microsserviços": ["microsservicos", "microservices", "microservicos", "micro servicos"],
    "mensageria": ["mensageria", "kafka", "rabbitmq", "sqs", "pub/sub", "message queue", "filas"],
    "serverless": ["serverless", "lambda", "cloud functions"],
    "arquitetura de software": ["arquitetura de software", "software architecture", "arquitetura de front-end", "arquitetura frontend", "frontend architecture", "clean architecture", "arquitetura", "architecture"],
    "system design": ["system design", "design de sistemas"],
    # infra
    "git": ["git", "github", "gitlab", "bitbucket"],
    "ci/cd": ["ci/cd", "ci", "cd", "continuous integration", "integracao continua", "github actions", "gitlab ci", "jenkins", "pipelines"],
    "docker": ["docker", "containers", "conteineres"],
    "kubernetes": ["kubernetes", "k8s", "eks", "gke"],
    "aws": ["aws", "amazon web services", "s3", "cloudfront", "ec2"],
    "gcp": ["gcp", "google cloud", "firebase"],
    "azure": ["azure"],
    "vercel": ["vercel", "netlify"],
    "terraform": ["terraform", "infraestrutura como codigo", "infrastructure as code", "iac"],
    "observabilidade": ["observabilidade", "observability", "monitoring", "monitoramento", "datadog", "sentry", "new relic", "grafana", "opentelemetry"],
    "feature flags": ["feature flags", "feature flag", "a/b testing", "testes a/b", "experimentation"],
    # IA
    "ia generativa": ["ia generativa", "generative ai", "genai", "inteligencia artificial", "artificial intelligence", "ai", "ia"],
    "llm": ["llm", "llms", "openai", "claude", "claude code", "cursor", "rag", "prompt engineering", "copilot", "github copilot", "ai agents", "agentes de ia", "ferramentas de ia", "ai tools", "ai-assisted"],
    # produto / design
    "figma": ["figma"],
    "ux": ["ux", "ui/ux", "user experience", "experiencia do usuario", "usabilidade"],
    "produto": ["product mindset", "visao de produto", "visao de negocio", "product thinking", "product-minded", "product sense", "business impact"],
    "segurança": ["seguranca", "security", "owasp", "seguranca da informacao", "appsec"],
    "gerenciamento de estado": ["gerenciamento de estado", "state management", "context api"],
    "analytics": ["analytics", "google analytics", "amplitude", "mixpanel", "metricas de produto"],
    # comportamentais / processo
    "agile": ["agile", "agil", "scrum", "kanban", "metodologias ageis"],
    "mentoria": ["mentoria", "mentoring", "mentorar", "mentor", "coaching"],
    "liderança técnica": ["lideranca tecnica", "tech lead", "technical leadership", "lider tecnico", "lideranca"],
    "comunicação": ["comunicacao", "communication", "communication skills"],
    "colaboração": ["colaboracao", "collaboration", "trabalho em equipe", "teamwork", "cross-functional", "multidisciplinar"],
    "inglês": ["ingles", "english", "ingles avancado", "ingles fluente", "fluent english", "advanced english"],
    "ownership": ["ownership", "autonomia", "protagonismo"],
    "documentação": ["documentacao", "documentation", "rfc", "adr"],
}

STOPWORDS = set("""
a o os as um uma uns umas de do da dos das em no na nos nas por para com sem sobre entre e ou que se
como mais menos muito muita ja nao sim ao aos pelo pela pelos pelas seu sua seus suas este esta isso
the and or of to in on for with by an at from as is are be this that it its we you our your will can
have has not but if their they them also more than other into such using use etc
""".split())

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9+#./-]*[a-z0-9+#]|[a-z0-9]")


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def norm(text: str) -> str:
    return " " + re.sub(r"\s+", " ", strip_accents(text or "").lower()) + " "


def _variant_pattern(v: str) -> re.Pattern:
    v = strip_accents(v.lower())
    return re.compile(r"(?<![a-z0-9#+.])" + re.escape(v) + r"(?![a-z0-9#+])")


_ALL_VARIANTS = sorted(
    ((strip_accents(v.lower()), canon, _variant_pattern(v)) for canon, vs in SYNONYMS.items() for v in vs),
    key=lambda x: -len(x[0]),
)


def find_terms(text: str, extra_terms: list[str] | None = None) -> Counter:
    """Conta termos canônicos no texto. Variações mais longas primeiro; o trecho
    casado é apagado para não contar 'react' dentro de 'react native' de novo."""
    t = norm(text)
    found: Counter = Counter()
    for _v, canon, pat in _ALL_VARIANTS:
        t, n = pat.subn(" \x00 ", t)
        if n:
            found[canon] += n
    for term in extra_terms or []:
        key = canonical(term)
        if key in found:
            continue
        hits = len(_variant_pattern(term).findall(t))
        if hits:
            found[key] += hits
    return found


def canonical(term: str) -> str:
    """Devolve o nome canônico de um termo, ou o próprio termo normalizado."""
    t = strip_accents(term.lower().strip())
    for canon, vs in SYNONYMS.items():
        if t == strip_accents(canon.lower()) or t in (strip_accents(v.lower()) for v in vs):
            return canon
    return term.lower().strip()


def tokens(text: str) -> list[str]:
    return [w for w in _WORD_RE.findall(norm(text)) if w not in STOPWORDS and len(w) > 1]


def tfidf_vectors(docs: list[str]) -> list[dict[str, float]]:
    toks = [tokens(d) for d in docs]
    df: Counter = Counter()
    for ts in toks:
        df.update(set(ts))
    n = len(docs)
    vecs = []
    for ts in toks:
        tf = Counter(ts)
        total = sum(tf.values()) or 1
        vec = {w: (c / total) * (math.log((1 + n) / (1 + df[w])) + 1) for w, c in tf.items()}
        vecs.append(vec)
    return vecs


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


METRIC_RE = re.compile(
    r"(\d+[.,]?\d*\s?%|\d+[.,]?\d*\s?(x|vezes|times)\b|r\$\s?\d|us\$\s?\d|\$\s?\d|\d+[.,]?\d*\s?(k|mil|mi|milh|million|m)\b"
    r"|\d+[.,]?\d*\s?(ms|s|segundos|seconds|horas|hours|dias|days|semanas|weeks|usuarios|users|clientes|customers|pessoas|devs|desenvolvedores)\b)",
    re.I,
)


def has_metric(text: str) -> bool:
    return bool(METRIC_RE.search(strip_accents(text or "")))


def split_bullets(text: str) -> list[str]:
    parts = re.split(r"(?:\n|^)\s*(?:[-•*·▪●]|\d+[.)])\s+|\n{1,}", text or "")
    parts = [p.strip() for p in parts if p and len(p.strip()) > 15]
    if len(parts) <= 1 and text and len(text) > 200:
        parts = [s.strip() for s in re.split(r"(?<=[.;])\s+", text) if len(s.strip()) > 15]
    return parts
