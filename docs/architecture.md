# Arquitetura atual

## Componentes

- `backend/app/routes/`: endpoints de saúde, pedidos, indicadores, previsão e assistente.
- `backend/app/services/`: regras de pedidos, agregações, previsão e recuperação/geração.
- `backend/app/models/` e `backend/app/schemas/`: persistência SQLAlchemy e contratos Pydantic.
- `data/ifood_ai_copilot.db`: banco SQLite local criado automaticamente.
- PostgreSQL 16: alternativa executada por `docker compose up -d db`.

## Fluxo de dados

1. Os pedidos são validados pela API e persistidos via SQLAlchemy.
2. Indicadores e previsões consultam somente os pedidos do `restaurant_id` informado.
3. A previsão agrega contagens diárias históricas e ajusta uma regressão linear.
4. O assistente recupera até quatro trechos relevantes dos últimos 90 dias com TF-IDF.
5. Os trechos recuperados e a pergunta são enviados a um endpoint compatível com a API de chat completions. A chave de API é fornecida pelo ambiente, nunca persistida no banco.

## Configuração

- `DATABASE_URL`: URL SQLAlchemy. Sem configuração, usa SQLite na pasta `data/`.
- `LLM_API_KEY`: obrigatória para gerar respostas do assistente.
- `LLM_BASE_URL`: endpoint base do provedor, opcional (padrão: `https://api.openai.com/v1`).
- `LLM_MODEL`: nome do modelo, opcional (padrão: `gpt-4o-mini`).

O SQLite é destinado à execução local. Para PostgreSQL, inicie o serviço Compose
e configure `DATABASE_URL` no processo da API. O dashboard web, embeddings e
armazenamento vetorial continuam fora do escopo da implementação atual.
