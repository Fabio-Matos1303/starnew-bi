Starnew BI — Progresso de Sprints

Sprint 0 (concluída)
- Infra base: backend FastAPI 3.11 e frontend Vue 3 com Vite
- Nginx servindo build do frontend e proxy para `/api`
- Compose com serviços `backend` e `frontend`
- Integração de rede com `singre-docker` (`singre-docker_default`)
- Healthcheck `/api/v1/health` com verificação opcional do MySQL (read-only)

Sprint 1 (em andamento) — Base de API e OS
- Estrutura da API v1 com roteador modular e CORS
- Endpoints OS:
  - `GET /api/v1/os/status` — distribuição por status (filtros `from`/`to`)
  - `GET /api/v1/os/volume` — volume diário (filtros `from`/`to`)
  - `GET /api/v1/os/tempo-medio-conclusao` — TMC (filtros `from`/`to`)
  - `GET /api/v1/os/list` — listagem paginada por período e status
- Frontend: Tela `/os` com gráficos (ApexCharts) e listagem com paginação; filtros de período e drill‑down por status
- CI: workflow com build frontend e testes backend (pytest)

Próximos itens da Sprint 1
- Schemas Pydantic públicos/documentação no README
- Validação e normalização de parâmetros (ex.: status)
- Endpoint de “Top serviços” (a depender do modelo de itens de OS)
- Loading states/erros e polimento visual na tela de OS
Plano de sprints (foco em valor contínuo e integrações com SINGRE)

  • Duração sugerida: 1 semana por sprint (ajuste conforme equipe/disponibilidade)
  • Regra de ouro: sempre “demoável” ao final, com stack subindo via docker compose up e
    endpoints/telas funcionando


  Sprint 0 — Fundação e ambiente

  • Objetivo: tudo pronto para desenvolver e integrar ao MySQL do SINGRE (read-only)
  • Entregas:
    • Repositório estruturado (backend/, frontend/, docker-compose.yml, .env.example)
    • Compose do BI (backend FastAPI + frontend Vue + Nginx em prod) rodando local
    • Conexão ao MySQL do SINGRE via usuário somente leitura (porta 3307 ou rede
      compartilhada)
    • Observabilidade básica: logs estruturados, healthcheck
    • CI mínima (lint + testes básicos)
  • Critérios de aceite:
    • GET /api/v1/health responde OK e valida acesso ao DB
    • Frontend “Hello Dashboard” servido no :8080 (ou porta definida)


  Sprint 1 — Backend base (FastAPI + SQLAlchemy)

  • Objetivo: camada de API sólida, segura e configurável
  • Entregas:
    • Config centralizada (env vars), conexão pool MySQL, Pydantic schemas
    • Módulos core/, models/ (mapeamento essencial para Vendas/OS/Locações), api/
    • Tratamento de erros, CORS, versionamento /api/v1
    • Testes unitários e de integração (DB read-only)
  • Critérios de aceite:
    • 2-3 endpoints de exemplo com queries reais simples e testes automatizados
    • Cobertura mínima acordada (ex.: 60%)


  Sprint 2 — Frontend base (Vue 3 + PrimeVue + ApexCharts)

  • Objetivo: estrutura do dashboard e consumo da API
  • Entregas:
    • Layout, navegação (Home, Vendas, OS, Locações), tema consistente
    • Cliente HTTP, gestão de estado leve, .env do frontend
    • Componentes de gráficos (ApexCharts) e cards de KPI reutilizáveis
  • Critérios de aceite:
    • Home renderiza dados mockados e, em seguida, dados reais do endpoint de health
    • Build de produção servido pelo Nginx do container


  Sprint 3 — KPIs “Geral” (Home)

  • Objetivo: visão executiva funcionando com filtros de período
  • Entregas:
    • Endpoints: GET /kpi/geral (receita total, participação Vendas/OS/Locações, novos
      clientes, status de OS)
    • Filtros por período (ex.: mês atual, últimos 30 dias)
    • Cache leve de consultas (ex.: in-memory com TTL) e índices SQL críticos
    • Tela “Geral” com gráfico de linha, pizza/rosca e barras
  • Critérios de aceite:
    • Respostas em < 500ms para períodos típicos (ambiente dev)
    • Valores amostrados conferidos com consultas no phpMyAdmin


  Sprint 4 — Análise de Vendas

  • Objetivo: profundidade em vendas com comparativos
  • Entregas:
    • Endpoints: faturamento, ticket médio, top produtos, por categoria, por vendedor
    • Exportação CSV no backend para datasets tabulares
    • Tela “Vendas” com gráficos e tabela com paginação
  • Critérios de aceite:
    • Cálculos auditáveis (amostragem) e consistentes entre endpoints
    • Exportação CSV disponível e validada


  Sprint 5 — Análise de Ordens de Serviço (OS)

  • Objetivo: eficiência operacional e fluxo das OS
  • Entregas:
    • Endpoints: faturamento OS, volume, tempo médio de conclusão (TMC), top serviços,
      distribuição de status
    • Drill-down de OS por status
    • Tela “OS” com barras, linhas e distribuição
  • Critérios de aceite:
    • TMC validado por amostra e por SQL manual
    • Resiliência para OS sem datas completas (tratamento de nulos)


  Sprint 6 — Análise de Locações

  • Objetivo: rentabilidade e ocupação de ativos
  • Entregas:
    • Endpoints: faturamento, taxa de ocupação, top itens, duração média, receita por
      cliente
    • Tela “Locações” com indicadores e séries temporais
  • Critérios de aceite:
    • Cálculo da ocupação consistente com base instalada/contratada
    • Performance dentro das metas do projeto


  Sprint 7 — Segurança, hardening e UX final

  • Objetivo: pronto para usuários reais
  • Entregas:
    • Autenticação simples (ex.: JWT) ou proteção por rede/VPN conforme política
    • Rate limiting básico, headers de segurança e HTTPS no Nginx (se aplicável)
    • Polimento de UI/UX, loading states, vazios/erros
    • Documentação de uso e de API (OpenAPI enriquecida)
  • Critérios de aceite:
    • Check de segurança (secrets não comitados, usuário de DB read-only)
    • DX/UX: sem erros aparentes; manual de acesso e operação disponível


  Sprint 8 — Performance e dados

  • Objetivo: otimizar consultas e experiência
  • Entregas:
    • Tuning SQL, criação de views otimizadas ou data mart leve (somente leitura)
    • Cache mais robusto se necessário (ex.: Redis opcional)
    • Testes de carga e profiling das queries mais críticas
  • Critérios de aceite:
    • P95 dentro do alvo pactuado nas principais telas
    • Relatório breve de otimizações aplicadas e ganhos


  Dependências e riscos principais

  • Dependências: acesso ao MySQL do SINGRE (porta 3307 ou rede compartilhada), criação do
     usuário read-only, exemplos de consultas validadas no phpMyAdmin.
  • Riscos: performance em tabelas grandes sem índices/views; diferenças de schema;
    tecnologias legadas (MySQL 5.7) limitando recursos; políticas de segurança/infra.


  Definição de pronto (geral)

  • Código versionado, testado, com CI verde
  • Stack sobe via docker compose up e funciona
  • Telas e endpoints da sprint “demoáveis”
  • Documentação mínima atualizada no README.md
  • Se quiser, já começo pela Sprint 0 criando a estrutura do repositório, compose e
    healthcheck.
