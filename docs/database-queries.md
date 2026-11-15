# Consultas úteis ao banco SQLite

Este guia reúne consultas SQLite para explorar e analisar os pedidos do iFood
AI Copilot. O modelo atual persiste os dados na tabela `orders`.

## Conexão e esquema

Por padrão, a aplicação usa o arquivo SQLite `data/ifood_ai_copilot.db`, na
raiz do projeto. Abra esse arquivo em uma ferramenta compatível com SQLite,
como o DB Browser for SQLite ou uma extensão de SQLite no VS Code.

> **Importante:** execute somente as consultas do banco ao qual você está
> conectado. As consultas desta página são para SQLite; elas não usam a
> sintaxe específica de PostgreSQL.

### Listar tabelas

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

### Ver colunas de `orders`

```sql
PRAGMA table_info(orders);
```

Colunas atuais:

| Coluna | Tipo lógico | Observações |
| --- | --- | --- |
| `id` | texto (UUID) | Chave primária |
| `restaurant_id` | texto | Identificador do restaurante |
| `amount` | decimal | Valor do pedido |
| `items_count` | inteiro | Quantidade de itens |
| `status` | texto | `pending`, `preparing`, `delivered` ou `cancelled` |
| `created_at` | data/hora | Instante de criação; a aplicação usa UTC |

## Consultas de pedidos

Nos exemplos, troque `demo-restaurant` pelo `restaurant_id` desejado. A massa
de demonstração usa esse identificador por padrão.

### Ver pedidos mais recentes

```sql
SELECT id, restaurant_id, amount, items_count, status, created_at
FROM orders
WHERE restaurant_id = 'demo-restaurant'
ORDER BY created_at DESC, id
LIMIT 50;
```

### Buscar um pedido pelo identificador

```sql
SELECT id, restaurant_id, amount, items_count, status, created_at
FROM orders
WHERE restaurant_id = 'demo-restaurant'
  AND id = 'COLE-O-UUID-DO-PEDIDO-AQUI';
```

### Filtrar por status

```sql
SELECT id, amount, items_count, status, created_at
FROM orders
WHERE restaurant_id = 'demo-restaurant'
  AND status = 'pending'
ORDER BY created_at DESC;
```

### Consultar pedidos em um intervalo de datas

Use início inclusivo e fim exclusivo. Assim, o intervalo inclui o dia inicial
inteiro e não depende da precisão dos segundos no último dia. No SQLite da
aplicação, informe os limites em UTC.

```sql
SELECT id, amount, items_count, status, created_at
FROM orders
WHERE restaurant_id = 'demo-restaurant'
  AND created_at >= '2026-11-01 00:00:00'
  AND created_at <  '2026-12-01 00:00:00'
ORDER BY created_at;
```

Os valores de data/hora são armazenados sem informação de fuso pelo driver
SQLite, embora a aplicação trate os instantes como UTC.

## Indicadores operacionais

### Resumo geral de um restaurante

```sql
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    SUM(CASE WHEN status = 'delivered' THEN amount ELSE 0 END) AS revenue,
    AVG(CASE WHEN status = 'delivered' THEN amount END) AS average_order_value
FROM orders
WHERE restaurant_id = 'demo-restaurant';
```

A receita e o valor médio consideram somente pedidos `delivered`, como no
resumo operacional da API.

### Quantidade de pedidos por status

```sql
SELECT status, COUNT(*) AS total
FROM orders
WHERE restaurant_id = 'demo-restaurant'
GROUP BY status
ORDER BY total DESC, status;
```

### Vendas e pedidos por dia

```sql
SELECT
    date(created_at) AS order_date,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'delivered' THEN amount ELSE 0 END) AS revenue
FROM orders
WHERE restaurant_id = 'demo-restaurant'
GROUP BY date(created_at)
ORDER BY order_date;
```

### Pedidos por hora do dia

```sql
SELECT
    CAST(strftime('%H', created_at) AS INTEGER) AS hour_of_day,
    COUNT(*) AS total_orders
FROM orders
WHERE restaurant_id = 'demo-restaurant'
  AND status <> 'cancelled'
GROUP BY strftime('%H', created_at)
ORDER BY hour_of_day;
```

O resumo da API também exclui pedidos cancelados dessa métrica.

### Ticket médio e quantidade média de itens por status

```sql
SELECT
    status,
    COUNT(*) AS total_orders,
    AVG(amount) AS average_order_amount,
    AVG(items_count) AS average_items_per_order
FROM orders
WHERE restaurant_id = 'demo-restaurant'
GROUP BY status
ORDER BY status;
```

### Restaurantes com mais pedidos

```sql
SELECT
    restaurant_id,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'delivered' THEN amount ELSE 0 END) AS revenue
FROM orders
GROUP BY restaurant_id
ORDER BY total_orders DESC, restaurant_id
LIMIT 20;
```

## Verificações de dados

### Conferir status existentes

```sql
SELECT status, COUNT(*) AS total
FROM orders
GROUP BY status
ORDER BY status;
```

### Procurar valores fora das regras da API

A API exige valor positivo, ao menos um item e um dos quatro status válidos.
Esta consulta ajuda a encontrar registros que não respeitam essas regras:

```sql
SELECT id, restaurant_id, amount, items_count, status, created_at
FROM orders
WHERE amount <= 0
   OR items_count < 1
   OR status NOT IN ('pending', 'preparing', 'delivered', 'cancelled')
ORDER BY created_at DESC;
```

### Conferir pedidos sem restaurante ou data

```sql
SELECT id, restaurant_id, created_at
FROM orders
WHERE restaurant_id IS NULL
   OR restaurant_id = ''
   OR created_at IS NULL;
```

## Alterações manuais

Prefira criar ou alterar pedidos pela API. Se precisar editar dados diretamente,
confira primeiro o pedido com um `SELECT`, filtre sempre pelo restaurante e
pelo UUID, e faça a alteração dentro de uma transação. Não execute um `UPDATE`
ou `DELETE` sem a cláusula `WHERE`.

Exemplo de atualização de status no SQLite:

```sql
BEGIN;

UPDATE orders
SET status = 'delivered'
WHERE restaurant_id = 'demo-restaurant'
  AND id = 'COLE-O-UUID-DO-PEDIDO-AQUI';

-- Confira a alteração antes de confirmar:
SELECT id, restaurant_id, status
FROM orders
WHERE restaurant_id = 'demo-restaurant'
  AND id = 'COLE-O-UUID-DO-PEDIDO-AQUI';

-- Use COMMIT para confirmar ou ROLLBACK para desfazer.
COMMIT;
```

Para remover um pedido, use o mesmo filtro por restaurante e UUID em um
`DELETE`, após conferir o registro com `SELECT`. Essa operação é permanente
depois do `COMMIT`.

## Boas práticas

- Em código da aplicação, use consultas parametrizadas/SQLAlchemy; não monte
  SQL concatenando valores recebidos do usuário.
- Sempre filtre por `restaurant_id` ao consultar pedidos de um restaurante.
- Para intervalos de tempo, prefira `>= início` e `< fim`; use limites UTC.
- Teste `UPDATE` e `DELETE` em uma transação e confirme o resultado antes do
  `COMMIT`.
- As consultas refletem o modelo atual. Se novas tabelas ou colunas forem
  adicionadas, atualize este guia junto com os modelos.
