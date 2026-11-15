# 🤖 iFood AI Copilot

### Assistente inteligente para análise operacional de restaurantes utilizando Machine Learning, Generative AI e análise de dados.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Pytest-Testing-0A9EDC?logo=pytest" alt="Pytest">
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow" alt="Status">
</p>

---

## 📌 Sobre o projeto

O **iFood AI Copilot** é um projeto independente que propõe o desenvolvimento de um assistente inteligente para apoiar a gestão operacional de restaurantes por meio de dados e inteligência artificial.

A solução tem como objetivo transformar dados operacionais em informações estratégicas, permitindo identificar padrões, acompanhar indicadores, antecipar demandas e apoiar a tomada de decisões.

A proposta combina técnicas de **Machine Learning (ML)** e **Inteligência Artificial Generativa (GenAI)** para construir uma experiência em que os dados não sejam apenas apresentados, mas também interpretados por meio de recomendações inteligentes.

> Projeto de estudo e portfólio, desenvolvido de forma independente e inspirado em desafios do setor de restaurantes e delivery. Não possui vínculo ou integração oficial com o iFood.

## 🎯 Objetivos

- Desenvolver uma API para gerenciamento e consulta de dados operacionais.
- Analisar indicadores de desempenho dos restaurantes.
- Identificar padrões de pedidos e horários de maior movimento.
- Explorar modelos de Machine Learning para previsão de demanda.
- Desenvolver um assistente baseado em LLMs para interação com dados.
- Implementar uma arquitetura que permita evolução e escalabilidade.
- Aplicar boas práticas de desenvolvimento, testes automatizados e documentação.

## ✨ Funcionalidades

| Funcionalidade | Descrição | Status |
|---|---|---|
| API Backend | API REST com FastAPI | ✅ Implementada |
| Health Check | Monitoramento básico da API | ✅ Implementado |
| Testes automatizados | Testes de saúde, pedidos, indicadores, previsão e recuperação RAG | ✅ Implementado |
| Gerenciamento de pedidos | Cadastro, consulta, atualização e exclusão por restaurante | ✅ Implementado |
| Dashboard operacional | Indicadores, pedidos, previsão, assistente e navegação financeira | ✅ Implementado |
| Análise de dados | Resumo de pedidos, faturamento, status e horários de pico | ✅ Implementado |
| Machine Learning | Previsão diária de demanda com regressão linear | ✅ Implementado |
| Assistente GenAI | Agente Prato: perguntas em linguagem natural com Ollama local | ✅ Implementado |
| RAG | Recuperação TF-IDF de contexto operacional antes da geração | ✅ Implementado |

## 🏗️ Arquitetura

A arquitetura modular separa interface, backend, processamento inteligente e persistência de dados.

```text
                  ┌──────────────────────┐
                  │    Frontend Web      │
                  │   React + TypeScript │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │      FastAPI         │
                  │ Pedidos + Analytics  │
                  └──────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │ TF-IDF + LLM    │       │ scikit-learn    │
       │   RAG local     │       │ Demand Forecast │
       └────────┬────────┘       └────────┬────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                  ┌──────────────────────┐
                  │ SQLAlchemy + DB      │
                  │ SQLite / PostgreSQL  │
                  └──────────────────────┘
```

*A API usa SQLite em `data/` por padrão. PostgreSQL pode ser iniciado via Docker Compose.*

## 🛠️ Tecnologias

### Implementadas atualmente

- **Python:** linguagem principal do backend.
- **FastAPI:** construção da API REST.
- **SQLAlchemy:** persistência relacional com SQLite ou PostgreSQL.
- **PostgreSQL:** persistência para execução via Docker Compose.
- **scikit-learn:** previsão de pedidos e recuperação de contexto TF-IDF.
- **HTTPX:** chamadas assíncronas ao provedor de IA.
- **Ollama:** execução local pela API nativa, com geração concisa e sem thinking.
- **Pytest:** execução de testes automatizados.
- **React + TypeScript + Vite:** dashboard operacional responsivo.

### Tecnologias previstas

- **Embeddings e pgvector:** busca vetorial para evolução do RAG.

## 📂 Estrutura do projeto

Estrutura atual (a interface web ainda será adicionada):

```text
ifood-ai-copilot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .gitignore
│
├── frontend/             # Dashboard React + TypeScript
├── data/                 # Banco SQLite local (ignorado pelo Git)
├── collections/          # Coleções Bruno e Postman (local, ignorada pelo Git)
├── docs/
│   └── architecture.md
│
├── docker-compose.yml
└── README.md
```

*A base de dados SQLite local fica em `data/ifood_ai_copilot.db`.*

## ⚙️ Como executar localmente

### Pré-requisitos

- Python 3.10+
- Node.js 20+
- Git
- Visual Studio Code ou editor de sua preferência

### 1. Clone o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
```

### 2. Acesse a pasta do backend

```bash
cd ifood-ai-copilot/backend
```

### 3. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 4. Ative o ambiente virtual

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

### Configure a conta compartilhada de teste

Se ainda não existir, copie `.env.example` para `.env` na raiz do projeto;
se já existir, apenas acrescente as variáveis de autenticação. Defina um usuário
e uma senha para compartilhar com os testadores. Gere uma chave de autenticação com:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Preencha `PROTOTYPE_USERNAME`, `PROTOTYPE_PASSWORD` e `AUTH_SECRET_KEY` no
`.env`. `AUTH_RESTAURANT_ID` define qual restaurante a conta pode acessar
(`demo-restaurant` por padrão). Todos os testadores usam a mesma conta e os
mesmos dados; não compartilhe credenciais reais nem versione o arquivo `.env`.
Em hospedagem, configure esses valores como variáveis de ambiente e troque
`FRONTEND_ORIGINS` pela origem pública exata do dashboard. Use HTTPS na
hospedagem e não use esta conta compartilhada para dados reais de clientes.

### 6. Execute a aplicação (SQLite local)

Na pasta `backend`, execute:

```bash
python -m uvicorn app.main:app --reload
```

A API usa SQLite por padrão e cria `data/ifood_ai_copilot.db` na raiz do projeto.
O caminho é resolvido pela raiz do projeto e não depende da pasta atual do terminal.
Para usar PostgreSQL localmente, em outro terminal na raiz do projeto inicie o banco:

```bash
docker compose up -d db
```

No PowerShell, configure a conexão antes de iniciar a API:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://copilot:copilot@localhost:5432/ifood_ai_copilot"
```

Então inicie a API na pasta `backend` com o mesmo terminal:

```powershell
python -m uvicorn app.main:app --reload
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

O dashboard apresenta a tela de login. A API exige o token de autenticação nas
rotas de pedidos, indicadores e assistente; somente o health check e o login
são públicos.

### Executar o dashboard

Em outro terminal, instale as dependências e inicie o frontend:

```powershell
cd frontend
npm install
npm run dev
```

O dashboard ficará disponível em `http://127.0.0.1:5173`. Ele consulta a API
local em `http://127.0.0.1:8000`; para outro endereço, crie
`frontend/.env.local` com `VITE_API_BASE_URL=http://endereco-da-api`.
No filtro do dashboard, informe o mesmo identificador de restaurante usado ao
cadastrar os pedidos. A previsão só aparece quando há pedidos em pelo menos
dois dias do histórico; o assistente também requer o Ollama configurado.

### Gerar dados de demonstração

A API cria as tabelas do banco automaticamente ao iniciar, mas não insere pedidos
de demonstração. Para popular o banco com pedidos sintéticos distribuídos pelos
últimos 90 dias, execute na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m scripts.seed_demo_data
```

O restaurante padrão é `demo-restaurant`, igual ao filtro inicial do dashboard.
O script não apaga pedidos existentes e pode ser executado novamente sem
duplicar a massa. Para escolher outro restaurante ou período:

```powershell
.\.venv\Scripts\python.exe -m scripts.seed_demo_data --restaurant-id meu-restaurante --days 60
```

O script usa o mesmo `DATABASE_URL` da API. Se estiver usando PostgreSQL, defina
essa variável também no terminal que executa a carga.

Se o PowerShell não reconhecer `npm` após instalar o Node.js, feche e reabra o
terminal para atualizar o `PATH`. Se o Node estiver instalado em
`C:\Program Files\nodejs` e ainda não aparecer no `PATH`, use na sessão atual:

```powershell
$env:Path = "C:\Program Files\nodejs;$env:Path"
npm.cmd install
npm.cmd run dev
```

O uso de `npm.cmd` também evita a restrição de execução de scripts que pode
bloquear o atalho `npm.ps1` no PowerShell.

### 7. Acesse a documentação interativa

O FastAPI disponibiliza documentação automática por meio do Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 🧪 Testes automatizados

O projeto utiliza Pytest para validar o comportamento da aplicação.

Para executar os testes:

```bash
pytest
```

Para obter um relatório mais detalhado:

```bash
pytest -v
```

Os testes cobrem o health check, operações de pedidos, isolamento por restaurante,
indicadores e previsão de demanda. Para executá-los a partir da pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

## 🔌 Endpoints disponíveis

Coleções para testar a API no [Bruno e Postman](./collections/README.md).

### Health Check

Verifica se a aplicação está funcionando.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Verifica a saúde da API |
| POST | `/orders` | Cadastra um pedido |
| GET | `/orders?restaurant_id=...` | Lista pedidos com paginação |
| GET | `/orders/{id}?restaurant_id=...` | Consulta um pedido |
| PATCH | `/orders/{id}?restaurant_id=...` | Atualiza status, valor ou quantidade de itens |
| DELETE | `/orders/{id}?restaurant_id=...` | Exclui um pedido |
| GET | `/analytics/summary?restaurant_id=...` | Consulta indicadores; aceita `start_date` e `end_date` |
| GET | `/analytics/forecast?restaurant_id=...` | Prevê pedidos; aceita `days` e `history_days` |
| POST | `/assistant/ask` | Recupera contexto operacional e consulta o LLM |

Os status de pedido aceitos são `pending`, `preparing`, `delivered` e `cancelled`.
O faturamento considera somente pedidos entregues. A previsão precisa de pedidos
registrados em pelo menos dois dias do período histórico.

O `.env.example` usa Ollama local. Copie-o para `.env` na raiz do projeto e
inicie o Ollama com o modelo configurado para habilitar `/assistant/ask`:

```text
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen3:1.7b
```

Também é possível copiar `.env.example` para `.env` na raiz do projeto e
ajustar esses valores. O backend carrega esse arquivo automaticamente. No Ollama
local, `ollama` é apenas um valor de compatibilidade e não uma chave real. O
endpoint retorna HTTP 503 quando a variável não está configurada e 502 quando
o provedor falha. O `.env` é ignorado pelo Git; nunca versione credenciais.

Exemplo de resposta:

```json
{
  "status": "healthy",
  "application": "iFood AI Copilot"
}
```

## 🗺️ Roadmap de desenvolvimento

- [x] Criar repositório e estrutura inicial.
- [x] Configurar ambiente Python.
- [x] Inicializar API com FastAPI.
- [x] Implementar endpoint de Health Check.
- [x] Criar testes automatizados para a API.
- [x] Configurar persistência local e conexão opcional com PostgreSQL.
- [x] Implementar modelagem e endpoints de gerenciamento de pedidos.
- [x] Implementar indicadores operacionais.
- [x] Desenvolver previsão de demanda inicial.
- [x] Integrar IA Generativa via provedor configurável.
- [x] Implementar recuperação de contexto RAG com TF-IDF.
- [x] Desenvolver interface web para indicadores, pedidos, previsão e assistente.
- [ ] Evoluir RAG para embeddings e busca vetorial.
- [ ] Documentar e realizar deploy da aplicação.

## 💡 Diferenciais técnicos

O projeto busca explorar aspectos importantes da engenharia de software e da inteligência artificial:

- Arquitetura modular e organização de responsabilidades.
- Testes automatizados para aumentar a confiabilidade.
- Integração entre Machine Learning e IA Generativa.
- Respostas contextualizadas com recuperação de conhecimento.
- Avaliação da qualidade e confiabilidade das respostas geradas.
- Uso de dados sintéticos para experimentação e validação.

## 👩‍💻 Desenvolvedora

**Raiane Batista Silva Chaves**

Estudante de Engenharia de Software e desenvolvedora Backend em formação, com experiência em desenvolvimento de APIs, Java, Python e testes automatizados.

Atualmente, estagiária de Backend no PagBank, com interesse em Inteligência Artificial, Machine Learning, GenAI e soluções escaláveis.

- 💼 LinkedIn: [Raiane Batista](https://www.linkedin.com/in/raiane-batista-software-engineer/)
- 🐙 GitHub: [RaianeBatista](https://github.com/RaianeBatista)

---

<p align="center">
  Desenvolvido com dedicação, curiosidade e muita tecnologia. 💛
</p>
