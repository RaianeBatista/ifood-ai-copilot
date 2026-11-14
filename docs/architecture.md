# Arquitetura atual

## Componentes

- `backend/app/routes/`: endpoints de saúde, pedidos, indicadores, previsão e assistente.
- `backend/app/services/`: regras de pedidos, agregações, previsão e recuperação/geração.
- `backend/app/models/` e `backend/app/schemas/`: persistência SQLAlchemy e contratos Pydantic.
- `frontend/`: dashboard React + TypeScript para indicadores, pedidos recentes, previsão e assistente.
- `data/ifood_ai_copilot.db`: banco SQLite local criado automaticamente.
- PostgreSQL 16: alternativa executada por `docker compose up -d db`.

## Fluxo de dados

1. Os pedidos são validados pela API e persistidos via SQLAlchemy.
2. Indicadores e previsões consultam somente os pedidos do `restaurant_id` informado.
3. A previsão agrega contagens diárias históricas e ajusta uma regressão linear.
4. O assistente recupera até quatro trechos relevantes dos últimos 90 dias com TF-IDF.
5. Os trechos recuperados e a pergunta são enviados à API nativa do Ollama local. O thinking fica desativado e a geração é limitada a 120 tokens; no modo Ollama, `LLM_API_KEY=ollama` é apenas um valor de compatibilidade.
6. O dashboard consulta os endpoints de indicadores, pedidos, previsão e assistente. Em desenvolvimento, a API permite requisições CORS do Vite em `localhost:5173` e `127.0.0.1:5173`.

## Configuração

- `DATABASE_URL`: URL SQLAlchemy. Sem configuração, usa SQLite na pasta `data/`.
- `LLM_API_KEY`: obrigatória para gerar respostas do assistente.
- `LLM_BASE_URL`: URL base do Ollama local (padrão: `http://localhost:11434/v1`; a aplicação a converte para `/api/chat`).
- `LLM_MODEL`: nome do modelo local (padrão: `qwen3:1.7b`).

O SQLite é destinado à execução local. Para PostgreSQL, inicie o serviço Compose
e configure `DATABASE_URL` no processo da API. Embeddings e armazenamento
vetorial continuam fora do escopo da implementação atual.
