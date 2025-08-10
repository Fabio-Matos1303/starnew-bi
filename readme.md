# Starnew BI - Painel de Análise de Dados

## 1. Visão Geral do Projeto

Starnew Insights é um painel de dashboard analítico projetado para fornecer uma visão clara e estratégica dos dados operacionais da Starnew Informática. O projeto consome os dados do sistema de gestão interno (SINGRE) para gerar visualizações e métricas chave (KPIs), permitindo um acompanhamento preciso da saúde financeira e da performance de cada área de negócio.

O objetivo principal é transformar dados brutos em insights acionáveis, focando inicialmente em três áreas críticas: **Vendas**, **Ordens de Serviço (OS)** e **Locações**.

## 2. Arquitetura da Solução

A solução é baseada em uma arquitetura de microsserviços desacoplada, garantindo escalabilidade, manutenibilidade e flexibilidade.

### Fonte de Dados (Data Source)
- **Banco de Dados**: MySQL 5.7 (o mesmo utilizado pelo sistema SINGRE)
- **Acesso**: O acesso aos dados é feito de forma somente leitura (read-only) para garantir que o dashboard não possa, em nenhuma circunstância, alterar os dados operacionais da empresa

### Backend (API Layer)
- **Linguagem/Framework**: Python 3.10+ com FastAPI
- **Responsabilidade**: Criar uma API RESTful que expõe endpoints seguros para o frontend. A API contém toda a lógica de negócio: consulta o banco de dados, realiza os cálculos complexos para os KPIs (ex: ticket médio, tempo de conclusão de OS) e agrega os dados no formato que o frontend precisa
- **ORM/Conexão**: SQLAlchemy para uma interação segura e eficiente com o banco de dados MySQL

### Frontend (Presentation Layer)
- **Framework**: Vue.js 3 (com a Composition API)
- **Build Tool**: Vite para um desenvolvimento rápido e otimizado
- **Responsabilidade**: Construir a interface do usuário (o painel). Consome os dados da API Python e os renderiza em componentes interativos, como gráficos, tabelas e cartões de métricas

#### Bibliotecas de UI/Gráficos
- **UI Framework**: PrimeVue (sugestão) para um conjunto rico de componentes prontos (tabelas, menus, etc.)
- **Gráficos**: ApexCharts (via vue3-apexcharts) para visualizações de dados ricas e interativas

### Containerização
- **Ferramenta**: Docker e Docker Compose
- **Estrutura**: O projeto é totalmente containerizado. Um único comando (`docker compose up`) sobe todos os serviços necessários: o backend Python, o frontend Vue (servido via Nginx em produção) e, se necessário, uma instância do banco de dados para desenvolvimento

## 3. Estrutura de Diretórios do Projeto

A estrutura de pastas será organizada para separar claramente o backend do frontend.

```
starnew-bi/
├── backend/                  # Todo o código da API Python (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # Ponto de entrada da aplicação FastAPI
│   │   ├── core/             # Configurações, conexão com DB
│   │   ├── models/           # Modelos de dados (SQLAlchemy)
│   │   ├── schemas/          # Schemas de validação (Pydantic)
│   │   └── api/              # Endpoints da API (routers)
│   ├── Dockerfile            # Define a imagem Docker para o backend
│   └── requirements.txt      # Dependências Python
│
├── frontend/                 # Todo o código do Dashboard Vue.js
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/       # Componentes reutilizáveis (gráficos, cards)
│   │   ├── views/            # Páginas do dashboard (Home, Vendas, OS)
│   │   ├── services/         # Lógica para chamadas à API
│   │   ├── router/           # Rotas do Vue
│   │   └── main.js           # Ponto de entrada da aplicação Vue
│   ├── Dockerfile            # Define a imagem Docker para o frontend (build e Nginx)
│   └── package.json          # Dependências Node.js
│
├── docker-compose.yml        # Orquestra os contêineres (backend, frontend)
└── README.md                 # Este arquivo
```

## 4. Como Configurar e Rodar o Ambiente de Desenvolvimento

### Pré-requisitos
- Docker
- Docker Compose

### Passos para a Configuração

#### 1. Clonar o Repositório
```bash
git clone <url-do-repositorio>
cd starnew-insights
```

#### 2. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (`starnew-insights/`) a partir do exemplo `.env.example`. Este arquivo conterá as credenciais de acesso ao banco de dados do SINGRE.

**Arquivo `.env`:**
```env
# Credenciais do Banco de Dados do SINGRE
DB_HOST=mysql_singre_host  # Ex: host.docker.internal para acessar o MySQL do host
DB_PORT=3306
DB_USER=usuario_leitura
DB_PASSWORD=senha_segura
DB_NAME=starnew
```

> **Nota de Segurança**: É fundamental criar um usuário no MySQL (`usuario_leitura`) que tenha permissões de apenas `SELECT` nas tabelas do banco `starnew`.

#### 3. Subir os Serviços com Docker Compose
Execute o seguinte comando na raiz do projeto:

```bash
docker compose up --build -d
```

- `--build`: Força a reconstrução das imagens Docker na primeira vez
- `-d`: Roda os contêineres em modo "detached" (em segundo plano)

#### 4. Acessar a Aplicação
- **Dashboard (Frontend)**: http://localhost:8080
- **API (Backend Docs)**: http://localhost:8000/docs (Interface interativa do FastAPI para testar os endpoints)

## 5. Endpoints da API (Exemplos Iniciais)

A API Python (http://localhost:8000) fornecerá endpoints como:

### GET `/api/v1/health`
Verifica a saúde da API e a conexão com o banco.

### GET `/api/v1/kpi/geral`
Retorna as métricas principais para o dashboard geral.

**Exemplo de Resposta:**
```json
{
  "receita_total": 15000.50,
  "participacao": {
    "vendas": 7500.25,
    "os": 5000.00,
    "locacoes": 2500.25
  },
  "novos_clientes": 15,
  "os_status": {
    "abertas": 10,
    "em_andamento": 5,
    "concluidas": 25
  }
}
```

### GET `/api/v1/vendas/faturamento`
Retorna dados detalhados sobre o faturamento de vendas.

### GET `/api/v1/os/tempo-medio-conclusao`
Retorna o tempo médio para concluir uma Ordem de Serviço.

---

## Sugestões de Próximos Passos

1. **Vamos iniciar o desenvolvimento**: Posso criar a estrutura de diretórios e os arquivos Dockerfile e docker-compose.yml iniciais para você começar a codificar.

2. **Desenhar o Schema da API**: Podemos detalhar juntos os schemas (usando Pydantic no Python) para as respostas da API, garantindo que o frontend receba exatamente o que precisa.

3. **Criar a primeira consulta**: Com base no seu acesso ao phpMyAdmin, podemos pegar a estrutura da tabela vendas e criar a primeira consulta SQL real dentro da API Python.

---

> **Nota**: Este README.md estabelece uma base sólida para o projeto. Ele é um documento vivo e deve ser atualizado conforme novas funcionalidades, endpoints ou tecnologias forem adicionadas.
