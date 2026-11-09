# Como recrutadores e IA encontram e avaliam perfis do LinkedIn — mercado em novembro de 2026

Pesquisa feita em 2026-11-06. Foco: dev frontend sênior / fullstack, Brasil e exterior.

Legenda de confiabilidade:
- **[OFICIAL]**: página do LinkedIn (Help, Newsroom, Talent Blog, Engineering, business.linkedin.com) ou documentação do fornecedor.
- **[IMPRENSA]**: veículo jornalístico.
- **[BLOG]**: blog de terceiro, muitas vezes de um concorrente que vende ferramenta de sourcing. Trate como opinião ou como dado de segunda mão.
- **sem fonte**: não achei fonte primária para o número.

---

## Resumo (10 pontos mais importantes)

1. **Hoje a busca do Recruiter é por significado, não só por palavra-chave.** O recrutador escreve em linguagem natural ou cola a descrição da vaga. A IA transforma isso em filtros (cargo, local, competências) e o Advanced AI Search tenta casar "qualificações difíceis de definir" mesmo quando elas não aparecem literalmente no perfil. Cada candidato recebe um rótulo de relevância: High (≥70% das qualificações), Medium (≥30%) ou Low (<30%). [OFICIAL, LinkedIn Help a1660341, atualizado em 2026]
2. **O ranking usa, oficialmente:** competências padronizadas, empresas, escolas, semelhança da experiência com os critérios e **probabilidade de resposta**. Os pesos exatos não são públicos. Quem diz conhecê-los está chutando. [OFICIAL, a1660341]
3. **Hiring Assistant 2** foi anunciado em 29/09/2026 e chega automaticamente aos clientes em inglês a partir de novembro de 2026. Ele junta memória e raciocínio, verificação, apps conectados, triagem prévia por voz ou texto e dados do ATS (Greenhouse, Lever, SmartRecruiters…). O LinkedIn diz que recrutadores revisam 83% menos perfis e têm 4x mais chance de contatar candidatos achados pelo agente. [OFICIAL, news.linkedin.com/2026/hiring-assistant-2]
4. **"Interesse do candidato" é um sinal separado de "fit".** Segundo um blog que acompanha o produto, ele é alimentado por engajamento na plataforma, Open to Work e histórico de resposta a InMail. Perfil inativo e que não responde perde posição mesmo sendo bom. [BLOG, HeroHunt, 07/10/2026; sinal de "likely to respond" confirmado em OFICIAL a1660341]
5. **Verificação virou sinal de recrutamento, não só selo.** Existe o "Verified Applicant Spotlight" e os cards de candidato mostram os selos. Verificados recebem em média **60% mais visualizações de perfil**. Já são 115M de membros verificados. [OFICIAL]
6. **Open to Work (visível só para recrutadores) continua valendo.** A taxa de resposta a InMail desses candidatos é **37% maior**. [OFICIAL, Talent Blog, 19/05/2022, dados de 05/2021 a 04/2022]
7. **O LinkedIn também roda busca semântica do lado do membro.** A AI People Search foi lançada nos EUA em 13/11/2025. A AI Job Search em português chegou ao Brasil em jan/2026. O sistema usa recuperação por embeddings, um LLM como juiz de relevância e um modelo pequeno destilado. [OFICIAL/pesquisa: arXiv 2602.07309, LinkedIn, 07/02/2026]
8. **ATS brasileiros ranqueiam por aderência.** A Gaia, da Gupy, dá nota de afinidade de 0 a 100. A Sólides cruza o CV com a vaga e com o perfil comportamental. A Recrutei faz ranking por aderência. Gupy e InHire puxam perfis do LinkedIn por integração oficial (RSC) ou extensão do navegador. Na prática, o recrutador brasileiro ainda faz o hunting dentro do LinkedIn.
9. **Ferramentas de sourcing fora do LinkedIn** (Juicebox/PeopleGPT, SeekOut, hireEZ, Gem, Findem) indexam centenas de milhões de perfis públicos (LinkedIn, GitHub, Scholar…) com busca em linguagem natural. O LinkedIn está apertando o cerco jurídico: Proxycurl fechou em jul/2025 depois de processo, a ProAPIs foi processada em out/2025 e as páginas de Pin e Gem foram derrubadas em set/2026. GitHub e portfólio públicos também viram sinal de busca.
10. **Para texto:** título e cargo com o termo canônico em EN e PT ("Senior Frontend Engineer | Engenheiro Front-end Sênior"), competências padronizadas (até 100, as principais fixadas), experiência com stack explícita e métricas. Como a IA julga cada qualificação separadamente, cada requisito típico de vaga precisa estar escrito em algum lugar.

---

## Como o LinkedIn Recruiter ranqueia

### O que é oficial

**AI Search / Advanced AI Search (LinkedIn Recruiter)**. Fonte: LinkedIn Help a1660341, "Last updated: 1 week ago" em 11/2026. [OFICIAL]
- Entrada: prompt em linguagem natural. No Advanced AI Search, também aceita descrição da vaga, link da vaga ou notas de intake.
- Saída: filtros editáveis, mais um resumo de IA por candidato com rótulo **High / Medium / Low** conforme a porcentagem de qualificações atendidas.
- Dados usados no ranking: **perfil do membro e dados de rede (competências padronizadas, empresas, escolas)**, semelhança da experiência com os critérios e **probabilidade de o candidato responder**, além do feedback do recrutador (polegar para cima ou para baixo).
- Raça, gênero, nacionalidade, orientação sexual e idade não podem ser filtros.
- Busca em CV processa e padroniza **apenas currículos em inglês**.
- Usa Azure OpenAI. O resultado pode mudar entre sessões. A busca manual por palavra-chave e **booleana continua disponível** e pode ser usada no lugar da IA.
- Disponibilidade: AI Search está em Recruiter, RPS e RPS+. Advanced AI Search só em Recruiter e RPS+, com idioma em inglês.

**Hiring Assistant (v1)**. Disponível globalmente em inglês desde o fim de set/2025. [OFICIAL, news.linkedin.com, 03/09/2025]
- O próprio LinkedIn mede, com early adopters: 4h+ economizadas por vaga, 62% menos perfis revisados e +69% de aceitação de InMail.
- Arquitetura: um agente supervisor coordena subagentes de intake, sourcing, avaliação, outreach, triagem e memória. [OFICIAL, LinkedIn Engineering Blog, "How we engineered LinkedIn's Hiring Assistant"]
- Idiomas, segundo blog que cita a Help a7104929: holandês, inglês, francês, alemão, italiano, **português** e espanhol. [BLOG, HeroHunt]

**Hiring Assistant 2**. Anunciado em 29/09/2026 (Talent Connect). [OFICIAL, news.linkedin.com/2026/hiring-assistant-2; business.linkedin.com/talent-solutions/product-update/hire-release]
- Memória e raciocínio por vaga e por recrutador, com "sinais de fit além das qualificações".
- Mostra verificação, experiência relevante e **apps conectados** (o membro exibe trabalho de Behance, Replit, Medium etc. no perfil). Mostra também respostas de triagem prévia e dados do ATS.
- Verifica identidade e competências via ATS e integrações de terceiros e dá "mais transparência sobre como ranqueia".
- Números divulgados pelo LinkedIn: 83% menos perfis revisados, 4x mais chance de contato, top-match 2,6x mais entrevistado, triagem prévia com mediana de 6 min, mais de 20 mil empresas usando.
- Blog acrescenta: membros com app conectado recebem até **2,9x mais mensagens de recrutadores**, e há dados de GitHub e patentes desde mai/2026. [BLOG, HeroHunt, 07/10/2026; não confirmei na página oficial]

**Outros recursos da Release 2026** [OFICIAL, hire-release, sem data exata]
- **AI-Assisted Applicant Targeting**: extrai os requisitos obrigatórios da descrição da vaga.
- **Selo "Meets Targeting Criteria"**: atende ao local, a todas as competências obrigatórias e a pelo menos uma das preferidas. [OFICIAL, Help a1427105]
- **Verified Applicant Spotlight**.
- **AI-Assisted Search e Inbox redesenhados**.
- **CRM Connect**.

### Spotlights (filtros comportamentais)
Os Spotlights do Recruiter destacam subconjuntos como **Open to Work**, **mais propensos a responder / interessados na sua empresa**, engajados com a marca empregadora, ex-candidatos e candidatos internos. Em 2026 entrou o **Verified Applicant Spotlight**. [BLOG, leonar.app / foundrole; o Verified Spotlight é OFICIAL]

### Campos do perfil e peso provável
Não há documento oficial com pesos. A ordem abaixo é **inferência** cruzando a Help oficial com consenso de blogs:

| Campo | Como entra | Base |
|---|---|---|
| Cargo atual e anteriores (títulos) | Filtro de título e "related titles" sugeridos pela IA. É o primeiro campo que o recrutador lê | OFICIAL (filtros) + BLOG |
| Competências (padronizadas) | Explicitamente citadas como dado de ranking. Usadas no targeting de vaga (obrigatória / preferida) | OFICIAL |
| Experiência (texto e empresas) | "Similaridade da experiência com os critérios", interpretada semanticamente | OFICIAL |
| Título (headline) | Texto indexado e lido pela IA. Consenso de blog: campo de alto peso | BLOG |
| Sobre | Indexado pela busca semântica. Peso desconhecido | BLOG |
| Localização / aceita remoto | Filtro rígido. Obrigatório no "Meets Targeting Criteria" | OFICIAL |
| Open to Work | Spotlight, sinal de interesse, +37% de resposta | OFICIAL |
| Atividade e resposta a InMail | "Likely to respond" / interesse do candidato | OFICIAL (likely to respond) + BLOG (composição) |
| Verificação | Spotlight e selo no card | OFICIAL |
| Apps conectados (GitHub etc.) | Evidência no card do Hiring Assistant 2 | OFICIAL (conceito) + BLOG (números) |
| Premium do candidato | Não afeta ranking no Recruiter, segundo blogs | BLOG |

### Booleano
Continua disponível e é o caminho "reproduzível". Recrutadores técnicos ainda montam strings do tipo `("front-end" OR frontend OR "front end") AND (React OR Next.js) AND (TypeScript)`. Por isso grafias variantes (front-end, frontend, front end) e siglas mais nome por extenso continuam importando. [OFICIAL: Help a1660341 diz que a busca manual e booleana segue disponível; o exemplo é ilustrativo]

---

## Ferramentas de IA de sourcing/ATS

| Ferramenta | Região | O que lê | Usa IA semântica? | Origem dos dados / LinkedIn | Fonte |
|---|---|---|---|---|---|
| **LinkedIn Recruiter / Hiring Assistant** | Global | Perfil completo, competências padronizadas, rede, CV (só EN), atividade/resposta, verificação, apps conectados, ATS | Sim: LLM (Azure OpenAI), embeddings, LLM-juiz | Dados nativos | OFICIAL: Help a1660341; news 29/09/2026; arXiv 2602.07309 (07/02/2026) |
| **Gupy (Gaia)** | BR | CV/candidatura e respostas. Cruza com requisitos da vaga. Nota de afinidade 0–100 | Diz usar ML/PLN. Detalhes técnicos não públicos | Integração oficial **LinkedIn RSC** (1º ATS BR, nov/2024). Sincroniza a URL do perfil com dados públicos do LinkedIn | OFICIAL: gupy.io/integracao/integracao-linkedin-rsc; infográfico Gupy; blog Gupy (~2025); IMPRENSA: TechTudo 06/2026 (não elimina automaticamente, só ranqueia) |
| **Kenoby** (comprada pela Gupy) | BR | — | sem fonte atual | Incorporada à Gupy. Não achei documentação 2025–26 | sem fonte |
| **Sólides** | BR | CV versus descrição da vaga, mais o perfil comportamental (Profiler) | Diz usar IA de leitura de CV. Sem detalhe técnico | sem fonte sobre integração LinkedIn | OFICIAL (blog do fornecedor): solides.com.br/blog/inteligencia-artificial-no-recrutamento (sem data visível) |
| **InHire** | BR | Perfis do banco de talentos e da vaga, agentes de IA operacionais | Diz usar agentes de IA. Sem detalhe | **Extensão do Chrome no LinkedIn** (funciona com conta grátis ou paga) e importação em lote do Recruiter | OFICIAL: help.inhire.app; inhire.com.br/produto/ia |
| **Recrutei** | BR | CV e triagem. Ranking por aderência. Assistente "Rê" e bot no WhatsApp | Diz usar IA. Sem detalhe | sem fonte | OFICIAL: recrutei.com.br |
| **Greenhouse** | EUA/global | Candidatura, scorecards, transcrições de entrevista. Real Talent contra fraude | LLM em agentes de insight. Matching "assistivo". Rejeição só por regra configurada pelo cliente | ATS. Parceiro da avaliação via ATS do Hiring Assistant 2 | BLOG: HeroHunt 24/08/2026; BLOG HeroHunt 07/10/2026 |
| **Lever** | EUA/global | CV e candidatura | sem fonte específica | Parceiro de ATS do Hiring Assistant 2 | BLOG: HeroHunt 07/10/2026 |
| **Workday (+ HiredScore, Paradox)** | Global enterprise | CV e candidatura. HiredScore dá nota A–D com justificativa. Recruiter Agent busca passivos. Paradox/Olivia faz triagem conversacional | Sim (matching por IA explicável) | ATS. Integração HA2 "em breve". Paradox comprada em 01/10/2025 | BLOG: HeroHunt 24/08/2026 |
| **Ashby** | EUA/global (startups) | CV avaliado critério a critério **com citações do CV**. Redescoberta de talentos. Detecção de fraude (IP, device, e-mail) | Sim (LLM por critério) | ATS | BLOG: HeroHunt 24/08/2026; metaview |
| **Eightfold** | Global enterprise | CV, mais dados públicos complementares (redes sociais, histórico) e comparação com funcionários. Nota 0–5 | Sim, matching por competências (deep learning) | **Processo coletivo (Kistler v. Eightfold, 20/01/2026)** alega coleta de dados públicos sem aviso (FCRA). A Eightfold nega | IMPRENSA: Reuters via The Star/Yahoo 22/01/2026; JD Supra |
| **SeekOut** | EUA/global | 800M–1B perfis públicos, GitHub, publicações | Sim, busca semântica e booleana | Agrega dados públicos. Método de coleta não divulgado | BLOG: easyhireai, findem.ai (2026) |
| **hireEZ** (ex-Hiretual) | EUA/global | 45+ fontes de dados web | Sim, semântica e booleana | Agregação de perfis web | BLOG |
| **Gem** | EUA/global | Índice de 800M+ perfis, CRM, rediscovery | Sim, busca por IA e agentes | Página da empresa no LinkedIn **derrubada em set/2026** por suspeita de scraping (segundo ERE via HeroHunt) | OFICIAL: gem.com/solutions/enterprise; BLOG: HeroHunt 07/10/2026 |
| **Juicebox / PeopleGPT** | EUA/global | 600–800M perfis de mais de 30 fontes (LinkedIn, GitHub, Scholar, X) | Busca em linguagem natural com explicação do match. Uso de embeddings **sem fonte** | Indexa perfis públicos. Sem integração de InMail | BLOG: juicebox.ai/blog (do fornecedor), noon.ai |
| **Findem** | EUA/global | "Atributos" combinando dados de pessoas, empresas e mercado, mais 100k+ fontes | Sim, matching por atributos | Agregação | BLOG (do fornecedor): findem.ai/blog |
| **Fetcher** | EUA | Sourcing automatizado com outreach | sem fonte específica 2025–26 | sem fonte | sem fonte |
| **Paradox (Olivia)** | Global, alto volume | Conversa de triagem e agendamento | IA conversacional | Hoje é parte da Workday | BLOG: HeroHunt 24/08/2026 |

**Contexto de scraping** [IMPRENSA]
- **Proxycurl**: processada pelo LinkedIn em jan/2025, encerrou em jul/2025. Fontes: Bloomberg Law; Social Media Today; nubela.co/blog/goodbye-proxycurl.
- **ProAPIs**: processada em 03/10/2025 (N.D. Cal. 3:25-cv-08393).
- **Pin e Gem**: páginas de empresa derrubadas em set/2026.

Conclusão prática: o perfil do LinkedIn é lido (a) nativamente pelo Recruiter, (b) por ATS via RSC oficial ou extensão, e (c) por agregadores que também leem GitHub e sites pessoais.

---

## Números que importam

| Fator | Número | Fonte | Tipo / data |
|---|---|---|---|
| Foto de perfil | "Até **21x** mais visualizações e **9x** mais pedidos de conexão" | Texto do próprio LinkedIn exibido em perfis sem foto; LinkedIn Sales Blog "Picture Perfect" | OFICIAL, mas antigo (~2017–2019). Sem estudo atual |
| Foto (variações) | "14x mais encontrado", "36x mais mensagens" | Blogs que atribuem ao LinkedIn | BLOG. **Sem fonte primária** |
| Competências | ≥5 competências: **até 17x** mais visualizações | Anúncio do LinkedIn sobre endorsements, repostado (Goodreads/Sharlyn Lauby) | OFICIAL repostado, antigo (~2016) |
| Competências → recrutador | "até 33x mais contatado" | Blogs | **Sem fonte primária** |
| Limite de competências | **100** (só a seção Skills. As vinculadas a cargos não contam) | LinkedIn Help (answer 35265, segundo resultado de busca) | OFICIAL |
| Competências em destaque | Top 3 fixadas no perfil, e até 5 "top skills" no Sobre | Blogs | BLOG. Número exato (3 ou 5) não confirmado |
| Open to Work | Taxa de resposta a InMail **37%** maior | LinkedIn Talent Blog, 19/05/2022 | OFICIAL (dados 2021–22) |
| Open to Work (moldura pública) | ~40% mais InMails recebidos | Cognism 2025, citando dados do LinkedIn | BLOG. Não confirmado |
| Recommended Matches | Até 35% mais propensos a aceitar InMail | Talent Blog, 19/05/2022 | OFICIAL |
| InMail curto | <400 caracteres: +22% de resposta | Talent Blog, 19/05/2022 | OFICIAL (útil para entender o lado do recrutador) |
| Verificação | **+60%** de visualizações de perfil em média, ~+50% de engajamento | LinkedIn Help a1359065 (atualizado em 2026) | OFICIAL |
| Verificação (outlier) | ~90% mais visualizações | Social Media Today | IMPRENSA. Não confirmado |
| Membros verificados | 115M+ | LinkedIn via Social Media Today / HA2 | OFICIAL |
| Apps conectados | Até **2,9x** mais mensagens de recrutadores | HeroHunt citando o LinkedIn (HA2) | BLOG (não confirmei na fonte oficial) |
| Hiring Assistant 2 | 83% menos perfis revisados. 4x mais contato. Top-match 2,6x mais entrevistado | news.linkedin.com, 29/09/2026 | OFICIAL (dados próprios, sem auditoria) |
| Skills-based search | Empresas que mais buscam por competências têm 12% mais chance de contratação de qualidade | Future of Recruiting 2025 | OFICIAL |
| Mercado | Candidaturas por candidato +30% vs. pré-pandemia. Contratação global −30% | news.linkedin.com, 29/09/2026 | OFICIAL |
| Confiança | 64% dos TAs dos EUA acham mais difícil saber em quem confiar. 39%: "não saber se o candidato é real" | news.linkedin.com, 29/09/2026 | OFICIAL |
| Brasil | 100M de usuários no Brasil | Times Brasil, 30/06/2026 | IMPRENSA |
| Banner, recomendações, URL personalizada, perfil em 2º idioma, SSI, Top Voice → visualizações | — | — | **Sem fonte** com número 2025–26 |
| Posts / alcance em 2026 | Views médias por post caíram ~50%. Engajamento −25% | Richard van der Blom, Algorithm InSights (via vulse.co) | BLOG/relatório independente |

Observações:
- **SSI** ainda pode ser consultado de graça (Neal Schaffer, 2026, BLOG). Não há fonte de que o SSI influencie o ranking do Recruiter. Ele mede "social selling" e não é um sinal de recrutamento conhecido.
- **Top Voice**: o selo dourado de Community Top Voice acabou no fim de 2024. O azul segue só por convite e, em concessões novas, dura 6 meses com revisão periódica (Social Media Today; Blog du Modérateur). Não há fonte de que afete a busca do Recruiter.

---

## Boas práticas de texto

Base: consenso de blogs de 2025–26, mais o que a documentação oficial revela sobre como a busca funciona. Onde é inferência minha, está marcado.

1. **Título (headline)**
   - Nome canônico do cargo em EN e PT, stack principal e senioridade. Exemplo: `Senior Frontend Engineer | Engenheiro Front-end Sênior · React, TypeScript, Next.js · Fullstack Node.js`.
   - Evite título criativo ("Ninja do pixel"), porque nem o filtro de título nem o booleano vão casar.
2. **Cargo atual (campo Título da experiência)**
   - Use o título padronizado que o mercado busca: "Senior Frontend Engineer" / "Desenvolvedor Front-end Sênior". O filtro de título e os "related titles" da IA partem daqui. *Inferência a partir de OFICIAL a1660341.*
   - Se o título interno for estranho, acrescente o equivalente de mercado: "Software Engineer III (Senior Frontend)".
3. **Sobre**
   - 1ª frase: quem você é, com senioridade, anos e foco.
   - Depois: 3–5 resultados com métricas, stack em lista e o que você procura (remoto, fuso, tipo de vaga).
   - A busca semântica e o resumo de IA leem o texto, então frases claras com sujeito, ação e resultado funcionam melhor que listas soltas de buzzwords.
4. **Experiência com métricas**
   - Cada cargo: 3–6 bullets no formato verbo, o que fez, tecnologia e impacto numérico. Exemplos: "reduzi LCP de 4,1s para 1,8s com Next.js SSR"; "migrei 120 telas de JS para TypeScript".
   - Escreva **todos os requisitos típicos** da vaga-alvo: testes (Jest, Playwright), acessibilidade (WCAG), design system, CI/CD, performance, liderança técnica, mentoria. O Advanced AI Search e o Hiring Assistant avaliam qualificação por qualificação.
   - Vincule competências a cada cargo. Isso não consome o limite de 100. [OFICIAL]
5. **Competências**
   - Use os nomes padronizados da lista do LinkedIn ("React.js", "TypeScript", "Next.js", "Node.js", "Front-End Development").
   - Coloque as mais importantes no topo e fixe as 3 principais.
   - Ocupe bem os 100 slots com competências reais. A busca usa "competências padronizadas" e o targeting de vaga exige todas as obrigatórias. [OFICIAL]
6. **PT + EN e sinônimos**
   - Para vagas no exterior, mantenha o perfil principal em inglês e crie um perfil secundário em português (recurso nativo de perfil em outro idioma). Ou o contrário, se o foco for o Brasil.
   - O Recruiter faz busca em CV padronizada só em inglês. [OFICIAL]
   - Inclua as variantes: front-end / frontend / front end; fullstack / full-stack / full stack; JS / JavaScript; React / React.js; "Engenheiro de Software" / "Desenvolvedor". *Recomendação de BLOG, coerente com o uso de booleano.*
7. **Sinais de interesse e confiança**
   - Ative Open to Work visível só para recrutadores, com cargos, local e "remoto".
   - Verifique identidade e empresa.
   - Conecte apps (GitHub, portfólio).
   - Responda InMails, mesmo para recusar, porque a "probabilidade de resposta" entra no ranking. [OFICIAL]
8. **Coerência entre título, posts e perfil**
   - Blogs de 2026 relatam que o feed (modelo unificado, "360Brew") lê título, Sobre e experiência junto com os posts. Coerência temática ajuda alcance. [BLOG]
9. **Para ATS (Gupy etc.)**
   - CV em texto real, nada de imagem nem colunas complexas, com as palavras da vaga.
   - Nada de texto oculto ou "prompt injection": a Sólides cita isso como fraude detectável.

---

## Mudanças 2025–2026

| Data | Mudança | Fonte |
|---|---|---|
| jan/2025 | LinkedIn processa a Proxycurl (scraping). A empresa fecha em jul/2025 | IMPRENSA: Bloomberg Law; Social Media Today |
| mai/2025 | AI Job Search (linguagem natural) para Premium | IMPRENSA: Forbes, 02/06/2025 |
| 2025 | **Job Match**: mostra ao candidato como as qualificações dele casam com cada vaga. Premium vê "Top Applicant" | IMPRENSA: Social Media Today; BLOG: Interview Guys |
| 03/09/2025 | Hiring Assistant disponível globalmente em inglês (fim de set/2025) | OFICIAL: news.linkedin.com |
| 16/09/2025 | Ashby lança detecção de candidatos fraudulentos | BLOG: HeroHunt |
| 01/10/2025 | Workday conclui a compra da Paradox | BLOG: HeroHunt |
| 03/10/2025 | LinkedIn processa a ProAPIs | IMPRENSA: Bloomberg Law |
| 13/11/2025 | **AI People Search** (busca de pessoas em linguagem natural) para Premium nos EUA. Depois expandida para todos nos EUA. Sem previsão para o Brasil na época | IMPRENSA: TechCrunch, 13/11/2025; Canaltech, 13/11/2025 |
| 16/01/2026 | **Busca de vagas com IA em português** chega ao Brasil | IMPRENSA: MacMagazine, 16/01/2026; Fast Company Brasil |
| 20/01/2026 | Processo coletivo contra a Eightfold (pontuação "secreta", FCRA) | IMPRENSA: Reuters/The Star, 22/01/2026 |
| 07/02/2026 | Paper "Semantic Search at LinkedIn": LLM-juiz, embeddings e SLM destilado para AI Job Search e AI People Search | OFICIAL/pesquisa: arXiv 2602.07309 |
| ~mar/2026 | Feed passa a um modelo de ranking unificado por LLM | BLOG (vários). Não confirmado oficialmente |
| 2026 | Verificação: 115M+ membros. +60% de views. Verified Applicant Spotlight | OFICIAL: Help a1359065; hire-release |
| 2026 | Release de Hiring: AI-Assisted Applicant Targeting, AI Search redesenhada, CRM Connect | OFICIAL: business.linkedin.com/.../hire-release |
| jun/2026 | Hiring Assistant ganha francês e alemão (português já estava). Greenhouse lança 6 recursos de IA (10/06) | BLOG: HeroHunt |
| set/2026 | LinkedIn derruba as páginas de Pin e Gem (scraping) | BLOG: HeroHunt citando ERE |
| 29/09/2026 | **Hiring Assistant 2**: memória, fit e interesse, apps conectados, verificação, triagem por voz, avaliação via ATS. Rollout a partir de nov/2026 | OFICIAL: news.linkedin.com/2026/hiring-assistant-2 |

---

## Fontes

### Oficiais (LinkedIn e fornecedores)
- LinkedIn Help: AI Search no Recruiter, https://www.linkedin.com/help/recruiter/answer/a1660341 (atualizado em ~out–nov/2026)
- LinkedIn Help: Verificações, https://www.linkedin.com/help/linkedin/answer/a1359065 (atualizado em ~set/2026)
- LinkedIn Help: Targeting criteria, https://www.linkedin.com/help/recruiter/answer/a1427105 (sem data)
- LinkedIn Help: Skills (limite de 100), https://www.linkedin.com/help/linkedin/answer/35265 (sem data; conteúdo visto via resultado de busca)
- LinkedIn Newsroom: Hiring Assistant 2, https://news.linkedin.com/2026/hiring-assistant-2 (29/09/2026)
- LinkedIn Newsroom: Hiring Assistant globalmente disponível, https://news.linkedin.com/2025/hiring-assistant-globally-available (03/09/2025)
- LinkedIn Talent Solutions: 2026 Hiring Release, https://business.linkedin.com/talent-solutions/product-update/hire-release (2026, sem data exata)
- LinkedIn Hiring Assistant (produto), https://business.linkedin.com/hire/hiring-assistant (2026)
- LinkedIn Engineering: How we engineered Hiring Assistant, https://www.linkedin.com/blog/engineering/ai/how-we-engineered-linkedins-hiring-assistant (2025, data não verificada)
- LinkedIn Talent Blog: InMail response rates, https://www.linkedin.com/business/talent/blog/talent-strategy/these-inmails-get-best-response-rates (19/05/2022)
- LinkedIn Talent Blog: 5 Ways to Use AI-Assisted Search, https://www.linkedin.com/business/talent/blog/talent-acquisition/ways-to-use-new-ai-assisted-search-and-projects-in-linkedin-recruiter (~2024)
- LinkedIn Future of Recruiting 2025, https://business.linkedin.com/hire/resources/future-of-recruiting (2025)
- LinkedIn Sales Blog: Picture Perfect, https://www.linkedin.com/business/sales/blog/b2b-sales/picture-perfect--make-a-great-first-impression-with-your-linkedi (antigo, sem data visível)
- arXiv: Semantic Search At LinkedIn, https://arxiv.org/abs/2602.07309 (07/02/2026)
- arXiv: SLM serving for Semantic Job Search, https://arxiv.org/pdf/2510.22101 (out/2025)
- Gupy: integração LinkedIn RSC, https://www.gupy.io/integracao/integracao-linkedin-rsc (sem data)
- Gupy: infográfico IA, https://www.gupy.io/hubfs/Infografico-como-a-IA-da-gupy-atua-no-recrutamento.pdf (sem data)
- Gupy blog: como usar IA para recrutar, https://www.gupy.io/blog/como-usar-a-inteligencia-artificial-para-recrutar (~2025)
- LinkedIn: integração Gupy, https://business.linkedin.com/hire/hiring-integrations/gupy (sem data)
- InHire: produto IA, https://www.inhire.com.br/produto/ia; Help, https://help.inhire.app/pt-BR/articles/6871586-o-que-e-a-fonte-do-talento-no-inhire (sem data)
- Sólides blog: IA no recrutamento, https://solides.com.br/blog/inteligencia-artificial-no-recrutamento/ (sem data)
- Recrutei, https://recrutei.com.br/ (2026)
- Gem Enterprise, https://www.gem.com/solutions/enterprise (2026)

### Imprensa
- BusinessToday: LinkedIn wants AI to do it, https://www.businesstoday.in/jobs/story/recruiters-may-soon-stop-searching-for-candidates-linkedin-wants-ai-to-do-it-553287-2026-09-03 (03/09/2026)
- TechCrunch: AI-powered people search, https://techcrunch.com/2025/11/13/linkedin-adds-ai-powered-search-to-help-users-find-people (13/11/2025)
- Canaltech: IA do LinkedIn para buscar profissionais, https://canaltech.com.br/apps/ia-do-linkedin-entende-o-que-voce-diz-para-buscar-profissionais/ (13/11/2025)
- MacMagazine: busca de vagas com IA no Brasil, https://macmagazine.com.br/post/2026/01/16/linkedin-anuncia-busca-de-vagas-com-inteligencia-artificial-no-brasil/ (16/01/2026)
- Fast Company Brasil: LinkedIn amplia busca por vagas com IA, https://fastcompanybrasil.com/ia/procura-emprego-linkedin-amplia-busca-por-vagas-com-ajuda-da-ia/ (2026)
- Forbes: LinkedIn AI job search for Premium, https://www.forbes.com/sites/torconstantino/2025/06/02/linkedin-launches-ai-job-search-tool-for-premium-users/ (02/06/2025)
- Social Media Today: LinkedIn AI tools, https://www.socialmediatoday.com/news/linkedin-ai-tools-job-seekers-recruiters-smbs/737481/ (2024–25)
- Social Media Today: LinkedIn expands verifications, https://www.socialmediatoday.com/news/linkedin-expands-verifications/831212/ (2026)
- Social Media Today: Top Voice badge, https://www.socialmediatoday.com/news/linkedin-updates-top-voice-badge/738428/ (2025)
- TechTudo: mitos da Gupy, https://www.techtudo.com.br/google/amp/noticias/2026/06/quer-passar-na-gupy-especialistas-revelam-o-que-e-mito-e-o-que-funciona-edsoftwares.ghtml (06/2026)
- Terra: É possível vencer a Gupy?, https://www.terra.com.br/noticias/educacao/carreira/e-possivel-vencer-a-gupy-especialistas-explicam-logica-da-ia-de-recrutamento-e-selecao,89714154a1f76ac4c6e63d245b0963e4u0ul30ma.html (sem data verificada)
- Times Brasil: 100M de usuários no Brasil, https://timesbrasil.com.br/empresas-e-negocios/linkedin-chega-a-100-mi-de-usuarios-no-brasil-com-ia-no-centro-das-contratacoes-diz-milton-beck-diretor-para-a-america-latina/ (30/06/2026)
- Reuters via The Star: Eightfold sued, https://www.thestar.com.my/tech/tech-news/2026/01/22/ai-company-eightfold-sued-for-helping-companies-secretly-score-job-seekers (22/01/2026)
- JD Supra: Eightfold/FCRA, https://www.jdsupra.com/legalnews/groundbreaking-lawsuit-tests-whether-ai-7379594/ (01/2026)
- Bloomberg Law: LinkedIn vs scrapers, https://news.bloomberglaw.com/artificial-intelligence/linkedins-war-against-bot-scrapers-ramps-up-as-ai-gets-smarter (fim de 2025)
- Social Media Today: LinkedIn wins vs Proxycurl, https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/ (2025)
- Baguete: Gupy com tecnologia do LinkedIn, https://www.baguete.com.br/noticias/gupy-agora-com-tecnologia-do-linkedin (nov/2024)

### Blogs (opinião ou segunda mão; vários são de concorrentes)
- HeroHunt: LinkedIn Recruiter AI features, https://www.herohunt.ai/blog/linkedin-recruiter-new-ai-features/ (21/04/2025, atualizado em set/2026)
- HeroHunt: Hiring Assistant 2, https://www.herohunt.ai/blog/linkedin-hiring-assistant-2-2026-features-cost-limits/ (07/10/2026)
- HeroHunt: Agentic ATS 2026, https://www.herohunt.ai/blog/agentic-ats-2026-greenhouse-vs-ashby-vs-workday/ (24/08/2026)
- Pin: LinkedIn Recruiter new features, https://www.pin.com/blog/linkedin-recruiter-new-features/ (2026)
- noon.ai: LinkedIn Recruiter AI features 2026, https://www.noon.ai/blog/articles/09-linkedin-recruiter-ai-features-2026 (2026)
- leonar.app: Recruiter search filters, https://www.leonar.app/blog/linkedin-recruiter-search-filters/ (2026)
- resumefast.io: How Recruiter search works, https://www.resumefast.io/blog/linkedin-recruiter-algorithm (2026)
- foundrole: 8 signals, https://www.foundrole.com/blog/how-recruiters-use-linkedin (2026)
- easyhireai: Juicebox vs SeekOut vs Findem, https://easyhireai.com/blog/hr-technology/juicebox-vs-seekout-vs-findem (2026)
- findem.ai: LinkedIn Recruiter alternatives, https://www.findem.ai/blog/linkedin-recruiter-alternatives (2026)
- juicebox.ai: candidate sourcing tools, https://juicebox.ai/blog/candidate-sourcing-tools (2026)
- noon.ai: Juicebox review, https://www.noon.ai/blog/articles/262-juicebox-review (2026)
- cvaudit.com.br: Gupy usa IA?, https://cvaudit.com.br/blog/gupy-usa-inteligencia-artificial (2026)
- vulse.co: LinkedIn 2026 algorithm, https://vulse.co/blog/how-linkedin-2026-algorithm-works-and-what-it-means-for-your-content-strategy (2026)
- missivedigital: LinkedIn algorithm updates, https://missivedigital.com/linkedin-algorithm-updates/ (2026)
- Neal Schaffer: SSI, https://nealschaffer.com/weave-social-traditional-selling-strategies/ (2026)
- Interview Guys: Job Match, https://blog.theinterviewguys.com/linkedins-new-ai-job-match-tool/ (2025)
- Goodreads/Sharlyn Lauby: 17x skills (repost do LinkedIn), https://www.goodreads.com/author_blog_posts/14242312-linkedin-endorsements-user-profiles-receive-17-times-more-views (antigo)

### Lacunas honestas
- Pesos do ranking do Recruiter: **não publicados**.
- Números atuais (2025–26) para foto, banner, recomendações, URL personalizada e perfil em 2º idioma: **sem fonte**. Os de foto e competências são antigos.
- Kenoby e Fetcher: sem documentação 2025–26 encontrada.
- Uso de embeddings por Juicebox, Gupy, Sólides, Recrutei e InHire: **sem fonte técnica**.
