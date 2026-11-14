# Backend

API REST do iFood AI Copilot, construída com FastAPI.

## Preparar o ambiente (PowerShell)

Na pasta `backend`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação do ambiente, execute os comandos usando
`.\.venv\Scripts\python.exe` no lugar de `python`.

## Executar os testes

Instale as dependências de desenvolvimento e rode os testes com o Python do
ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

## Executar

```powershell
python -m uvicorn app.main:app --reload
```

O servidor inicia em `http://127.0.0.1:8000`. A documentação interativa fica
em `http://127.0.0.1:8000/docs` e o endpoint de saúde em
`http://127.0.0.1:8000/health`.

Por padrão, a API cria o banco SQLite em `data\ifood_ai_copilot.db`, na raiz
do projeto. Para usar PostgreSQL, inicie-o na raiz do projeto:

```powershell
docker compose up -d db
$env:DATABASE_URL = "postgresql+psycopg://copilot:copilot@localhost:5432/ifood_ai_copilot"
```

As credenciais definidas no Compose são somente para desenvolvimento local.
Configure credenciais próprias em qualquer ambiente compartilhado ou de produção.

Se estiver usando o ambiente virtual do projeto, também é possível iniciar a
API pelo terminal do PowerShell, na pasta `backend`, com:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Endpoints

- `POST`, `GET`, `PATCH` e `DELETE /orders`: gerenciamento de pedidos; informe
  `restaurant_id` nas consultas, atualizações e exclusões.
- `GET /analytics/summary`: indicadores operacionais por restaurante e período.
- `GET /analytics/forecast`: previsão diária; requer pedidos em pelo menos dois
  dias do histórico.
- `POST /assistant/ask`: RAG e geração via provedor OpenAI-compatible; requer
  `LLM_API_KEY`. `LLM_BASE_URL` e `LLM_MODEL` são opcionais.

## Estrutura

```text
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── schemas/
├── tests/         # Testes automatizados
├── requirements.txt
└── requirements-dev.txt
```
